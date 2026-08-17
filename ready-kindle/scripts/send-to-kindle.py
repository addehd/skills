#!/usr/bin/env python3
"""Send an EPUB to Kindle via SMTP using Hermes email creds.

Reads EMAIL_ADDRESS / EMAIL_PASSWORD / EMAIL_SMTP_HOST / EMAIL_SMTP_PORT /
EMAIL_SENDER_NAME from ~/.hermes/.env. Usage:

    send-to-kindle.py <file.epub> [subject]
"""
import os
import smtplib
import ssl
import sys
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path

KINDLE_ADDRESS = "adolfo.heriz.ocampo_QSaEKm@kindle.com"


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


def main() -> int:
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <file.epub> [subject]", file=sys.stderr)
        return 2

    epub = Path(sys.argv[1]).expanduser()
    subject = sys.argv[2] if len(sys.argv) > 2 else epub.stem
    if not epub.is_file():
        print(f"error: file not found: {epub}", file=sys.stderr)
        return 1
    if epub.suffix.lower() != ".epub":
        print("warning: Amazon's Send-to-Kindle rejects .mobi; use EPUB", file=sys.stderr)

    env = load_env(Path.home() / ".hermes" / ".env")
    sender = env.get("EMAIL_ADDRESS", "").strip()
    password = env.get("EMAIL_PASSWORD", "").strip()
    smtp_host = env.get("EMAIL_SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(env.get("EMAIL_SMTP_PORT", "587"))
    sender_name = env.get("EMAIL_SENDER_NAME", "").strip()

    if not sender or not password:
        print("error: EMAIL_ADDRESS / EMAIL_PASSWORD missing from ~/.hermes/.env", file=sys.stderr)
        return 1

    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{sender}>" if sender_name else sender
    msg["To"] = KINDLE_ADDRESS
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)

    body = MIMEText(
        f"Sent by ready-kindle skill.\n\nFile: {epub.name}\n"
        f"Convert this document to your Kindle format."
    )
    msg.attach(body)

    with epub.open("rb") as fh:
        att = MIMEApplication(fh.read(), _subtype="epub+zip")
    att.add_header("Content-Disposition", "attachment", filename=epub.name)
    msg.attach(att)

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, context=ssl.create_default_context())
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls(context=ssl.create_default_context())
        with server:
            server.login(sender, password)
            server.sendmail(sender, [KINDLE_ADDRESS], msg.as_string())
    except Exception as e:
        print(f"error: SMTP send failed: {e}", file=sys.stderr)
        return 1

    print(f"sent: {epub.name} -> {KINDLE_ADDRESS} (subject: {subject})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
