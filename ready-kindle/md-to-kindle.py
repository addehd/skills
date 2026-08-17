#!/usr/bin/env python3
"""md-to-kindle: convert Markdown to EPUB and email it to your Kindle.

One command, no external tools (stdlib only): takes a .md file, builds an
EPUB, and sends it via SMTP to the Kindle address.

Config is read from ~/.hermes/.env:
    EMAIL_ADDRESS        sender (must be on Amazon's approved list)
    EMAIL_PASSWORD       app password
    EMAIL_SMTP_HOST      default smtp.gmail.com
    EMAIL_SMTP_PORT      default 587
    EMAIL_SENDER_NAME    optional display name
    EMAIL_KINDLE_ADDRESS optional; defaults to the known Kindle address

Usage:
    md-to-kindle.py <file.md> [subject]
"""
import os
import re
import smtplib
import ssl
import sys
import tempfile
import zipfile
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path

DEFAULT_KINDLE = "adolfo.heriz.ocampo_QSaEKm@kindle.com"

# ── config ────────────────────────────────────────────────────────────────

def load_env(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


# ── tiny markdown → HTML (good enough for documents) ─────────────────────

_INLINE = [
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"\*([^*]+)\*"), r"<em>\1</em>"),
    (re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)"), r'<a href="\2">\1</a>'),
]


def _inline(text: str) -> str:
    for pat, repl in _INLINE:
        text = pat.sub(repl, text)
    return text


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def md_to_html(md_text: str) -> str:
    """Convert a Markdown document to a single XHTML body fragment."""
    out: list[str] = []
    in_code = False
    code_lines: list[str] = []

    for line in md_text.splitlines():
        if line.strip().startswith("```"):
            if in_code:
                out.append(f"<pre>{_escape(chr(10).join(code_lines))}</pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue

        s = line.rstrip()
        if not s:
            continue
        if s.startswith("# "):
            out.append(f"<h1>{_inline(s[2:])}</h1>")
        elif s.startswith("## "):
            out.append(f"<h2>{_inline(s[3:])}</h2>")
        elif s.startswith("### "):
            out.append(f"<h3>{_inline(s[4:])}</h3>")
        elif s.startswith("#### "):
            out.append(f"<h4>{_inline(s[5:])}</h4>")
        elif s.startswith("- ") or s.startswith("* "):
            out.append(f"<li>{_inline(s[2:])}</li>")
        else:
            out.append(f"<p>{_inline(s)}</p>")

    if in_code:
        out.append(f"<pre>{_escape(chr(10).join(code_lines))}</pre>")

    body = "\n".join(out)
    # wrap loose <li> runs in a <ul>
    body = re.sub(r"(<li>.*?</li>)(?=\s*<li>|\s*$)", r"<ul>\1</ul>", body, flags=re.S)
    return body


# ── EPUB writer (EPUB 2, accepted by Send-to-Kindle) ─────────────────────

def build_epub(md_text: str, title: str, out_path: Path) -> None:
    body = md_to_html(md_text)
    content = f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{_escape(title)}</title></head>
<body>
{body}
</body>
</html>"""
    container = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{_escape(title)}</dc:title>
    <dc:language>en</dc:language>
    <dc:identifier id="uid">urn:uuid:md2kindle-{abs(hash(title))}</dc:identifier>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="chapter1"/>
  </spine>
</package>"""
    ncx = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content="urn:uuid:md2kindle-{abs(hash(title))}"/></head>
  <docTitle><text>{_escape(title)}</text></docTitle>
  <navMap><navPoint id="p1" playOrder="1"><navLabel><text>{_escape(title)}</text></navLabel><content src="chapter1.xhtml"/></navPoint></navMap>
</ncx>"""

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container)
        z.writestr("OEBPS/content.opf", opf)
        z.writestr("OEBPS/toc.ncx", ncx)
        z.writestr("OEBPS/chapter1.xhtml", content)


# ── send ─────────────────────────────────────────────────────────────────

def send_epub(env: dict, epub_path: Path, subject: str) -> None:
    sender = env.get("EMAIL_ADDRESS", "").strip()
    password = env.get("EMAIL_PASSWORD", "").strip()
    kindle = env.get("EMAIL_KINDLE_ADDRESS", DEFAULT_KINDLE).strip()
    smtp_host = env.get("EMAIL_SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(env.get("EMAIL_SMTP_PORT", "587"))
    sender_name = env.get("EMAIL_SENDER_NAME", "").strip()

    if not sender or not password:
        print("error: EMAIL_ADDRESS / EMAIL_PASSWORD missing from ~/.hermes/.env", file=sys.stderr)
        sys.exit(1)

    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{sender}>" if sender_name else sender
    msg["To"] = kindle
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg.attach(MIMEText(f"Converted by md-to-kindle.\n\nFile: {epub_path.name}"))

    with epub_path.open("rb") as fh:
        att = MIMEApplication(fh.read(), _subtype="epub+zip")
    att.add_header("Content-Disposition", "attachment", filename=epub_path.name)
    msg.attach(att)

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, context=ssl.create_default_context())
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls(context=ssl.create_default_context())
        with server:
            server.login(sender, password)
            server.sendmail(sender, [kindle], msg.as_string())
    except Exception as e:
        print(f"error: SMTP send failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> int:
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <file.md> [subject]", file=sys.stderr)
        return 2

    md_file = Path(sys.argv[1]).expanduser()
    subject = sys.argv[2] if len(sys.argv) > 2 else md_file.stem
    if not md_file.is_file():
        print(f"error: file not found: {md_file}", file=sys.stderr)
        return 1

    env = load_env(Path.home() / ".hermes" / ".env")

    with tempfile.TemporaryDirectory() as td:
        epub = Path(td) / f"{md_file.stem}.epub"
        build_epub(md_file.read_text(), subject, epub)
        send_epub(env, epub, subject)

    print(f"sent: {md_file.name} -> {env.get('EMAIL_KINDLE_ADDRESS', DEFAULT_KINDLE)} (subject: {subject})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
