---
name: ready-kindle
description: >-
  Converts Markdown to Kindle EPUB and emails it straight to the user's
  Kindle in one command (md-to-kindle.py in this repo — stdlib only, no
  Calibre/Go needed). Use when the user wants a Markdown document on their
  Kindle, mentions Kindle, EPUB, Send-to-Kindle, or md-to-kindle.
---

# Markdown to Kindle

One command converts Markdown to EPUB and emails it to the Kindle:

```bash
~/dev/skills/ready-kindle/md-to-kindle.py ~/md/my-doc.md "my-doc"
```

- **Input**: any `.md` file
- **Subject**: optional; defaults to the file name
- **Output**: EPUB attached to an email → Amazon delivers it to the Kindle
- **No installs**: pure Python stdlib (zipfile + smtplib)

## When to use

- User wants a document **sent to their Kindle**
- User mentions Kindle, EPUB, Send-to-Kindle, or `md-to-kindle`
- User has a Markdown doc they want to read on-device

## Configuration

All config comes from `~/.hermes/.env` (same file as the Hermes email
gateway). Nothing else to set up:

| Variable | Purpose | Default |
|----------|---------|---------|
| `EMAIL_ADDRESS` | Sender (must be on Amazon's approved list) | required |
| `EMAIL_PASSWORD` | Gmail app password | required |
| `EMAIL_KINDLE_ADDRESS` | Destination Kindle address | `adolfo.heriz.ocampo_QSaEKm@kindle.com` |
| `EMAIL_SMTP_HOST` | SMTP host | `smtp.gmail.com` |
| `EMAIL_SMTP_PORT` | SMTP port | `587` |
| `EMAIL_SENDER_NAME` | From display name | none |

The default Kindle address is already correct; you only touch config if you
change Kindle or email account.

## How it works

1. Converts Markdown to a minimal EPUB 2 (headings, paragraphs, lists, code
   blocks, inline bold/code/links) using only the Python standard library.
2. Attaches the EPUB to an email from `EMAIL_ADDRESS`.
3. Sends via SMTP (STARTTLS, or implicit TLS on port 465).

Amazon's Send-to-Kindle accepts EPUB and rejects `.mobi` (dropped 2022), so
this flow only produces EPUB.

## Pitfalls

- **Email never arrives** — confirm `EMAIL_ADDRESS` is on Amazon's Approved
  Personal Document E-mail List, and check `EMAIL_PASSWORD` is an app
  password (2FA breaks plain passwords).
- **Send is fire-and-forget** — success means queued to SMTP, not delivered
  to the device; Kindle delivery can take a minute or two.
- **Old tool** — the repo still contains `read/` (the Go `ready` CLI and
  Calibre-based MOBI path) from before; prefer `md-to-kindle.py` for the
  email flow. The old Apple Mail / osascript flow is obsolete.
