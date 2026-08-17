---
name: ready-kindle
description: >-
  Converts Markdown to Kindle MOBI or EPUB using the `ready` CLI from this
  repository (`read/main.go`, `read/install.sh`), with a fixed layout under
  `~/md/` and `~/md/kindle/`, and emails the EPUB straight to the user's
  Kindle via SMTP using the Hermes email account. Use when the user wants
  Kindle-compatible output, MOBI/EPUB from Markdown, wants a document sent
  to their Kindle, mentions `ready`, Calibre, or md/kindle folders.
---

# Markdown to Kindle via `ready`

This Skill file lives in the **`skills` repository**; the tool source is in
the `read/` subfolder (`read/main.go`, `read/install.sh`). Build and install
from that subfolder.

## When to use

- Converting Markdown to **MOBI** (Kindle) or **EPUB**
- User wants a document **sent/emailed to their Kindle** (see *Email to Kindle* below)
- User mentions **`ready`**, this repo, **Calibre**, or **`~/md`** / **`kindle`**

## Tool location and install

- **Repository**: `~/dev/skills/` — tool source in `read/`.
- **Install**: from `~/dev/skills/read/`, run `./install.sh` — builds with Go
  and copies to **`~/bin/ready`**.
- **PATH**: ensure `~/bin` is on `PATH` (e.g. `export PATH="$HOME/bin:$PATH"` in shell config).

## Prerequisites

| Need | Notes |
|------|--------|
| Go 1.21+ | To build via `install.sh` or `go build -o ready main.go` |
| `ready` on PATH | Typically `~/bin/ready` after install |
| Calibre (MOBI only) | Provides `ebook-convert`; Arch: `sudo pacman -S calibre` |

**EPUB-only**: Calibre is not required for the final EPUB file; `ready` writes
EPUB directly. **MOBI** always uses Calibre's `ebook-convert` after an
internal EPUB step.

## Folder convention (default)

Keep sources and outputs predictable:

| Role | Path |
|------|------|
| Source Markdown | `~/md/<name>.md` |
| Kindle / export | `~/md/kindle/<name>.mobi` or `.epub` |

Do not assume a different layout unless the user specifies one.

## Workflow

1. Save the Markdown file under **`~/md/<name>.md`**.
2. Ensure the output directory exists: `mkdir -p ~/md/kindle`.
3. Run **`ready`** with **explicit `-output`** so the MOBI/EPUB lands in
   `kindle/` (omitting `-output` places the file next to the input).

### MOBI (default format)

```bash
mkdir -p ~/md/kindle
ready -input ~/md/my-doc.md -output ~/md/kindle/my-doc.mobi
```

### EPUB

```bash
mkdir -p ~/md/kindle
ready -input ~/md/my-doc.md -format epub -output ~/md/kindle/my-doc.epub
```

### CLI reference

- **`-input`** — input `.md` file (required)
- **`-format`** — `mobi` or `epub` (default: `mobi`)
- **`-output`** — output path (recommended for `md/kindle/` layout)

## Email to Kindle

When the user wants the document delivered to their Kindle (the default when
they ask to "send" something to Kindle), email the file via SMTP after
converting.

- **Kindle address**: `adolfo.heriz.ocampo_QSaEKm@kindle.com`
- **Format must be EPUB.** Amazon's Send-to-Kindle email rejects `.mobi`
  attachments (dropped in 2022). Always convert with `-format epub` for this
  flow — Calibre is not needed.
- **Sender**: the Hermes email account (`adolfo.heriz.ocampo@gmail.com`,
  configured via `EMAIL_ADDRESS` in `~/.hermes/.env`), which must be on
  Amazon's Approved Personal Document E-mail List.

### Workflow

1. Convert to EPUB into the usual layout:

   ```bash
   mkdir -p ~/md/kindle
   ready -input ~/md/my-doc.md -format epub -output ~/md/kindle/my-doc.epub
   ```

2. Send it with the helper script (reads SMTP creds from `~/.hermes/.env`):

   ```bash
   ~/dev/skills/ready-kindle/scripts/send-to-kindle.py \
     ~/md/kindle/my-doc.epub "my-doc"
   ```

   The script attaches the EPUB as `my-doc.epub` and sends from
   `EMAIL_ADDRESS` to the Kindle address above. It honours
   `EMAIL_SENDER_NAME` for the From display name.

### Email pitfalls

- **Send is fire-and-forget** — success means queued, not delivered. If the
  document never arrives, check the SMTP response and that the sender is on
  Amazon's approved list.
- **MOBI attachment** — if a `.mobi` was emailed by mistake, Amazon bounces
  or silently drops it; re-send as EPUB.
- **Wrong sender** — `EMAIL_ADDRESS` in `~/.hermes/.env` must be the Gmail
  address approved by Amazon. Do not invent or substitute another address.

## Pitfalls

- **`ready` not found** — build/install from `~/dev/skills/read/`
  (`./install.sh`) and confirm `~/bin` on PATH.
- **MOBI errors about `ebook-convert`** — install Calibre; MOBI conversion
  depends on it.
- **Wrong output location** — without `-output`, the default is beside the
  input file; use `-output ~/md/kindle/...` for this workflow.
- **Old paths** — this skill previously targeted macOS (`~/Desktop/md`,
  Apple Mail, `osascript`). On Linux use `~/md` and the SMTP helper.
