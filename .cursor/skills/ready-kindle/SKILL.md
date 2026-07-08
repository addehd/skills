---
name: ready-kindle
description: >-
  Converts Markdown to Kindle MOBI or EPUB using the `ready` CLI from this
  repository (`install.sh`, `main.go`), with a fixed layout under
  `~/Desktop/md/` and `~/Desktop/md/kindle/`, and can email the EPUB
  straight to the user's Kindle via Apple Mail. Use when the user wants
  Kindle-compatible output, MOBI/EPUB from Markdown, wants a document sent
  to their Kindle, mentions `ready`, Calibre, or Desktop md/kindle folders.
---

# Markdown to Kindle via `ready`

This Skill file lives in the **`read` repository** next to `main.go` and `install.sh`. Build and install from that root.

## When to use

- Converting Markdown to **MOBI** (Kindle) or **EPUB**
- User wants a document **sent/emailed to their Kindle** (see *Email to Kindle* below)
- User mentions **`ready`**, this repo, **Calibre**, or **`~/Desktop/md`** / **`kindle`**

## Tool location and install

- **Repository**: the directory containing `main.go` and `install.sh` (this repo; often checked out at `/Users/addehd/dev/read/`).
- **Install**: from that directory, run `./install.sh` — builds with Go and copies **`~/bin/ready`**.
- **PATH**: ensure `~/bin` is on `PATH` (e.g. `export PATH="$HOME/bin:$PATH"` in shell config).

## Prerequisites

| Need | Notes |
|------|--------|
| Go 1.21+ | To build via `install.sh` or `go build -o ready main.go` |
| `ready` on PATH | Typically `~/bin/ready` after install |
| Calibre (MOBI only) | Provides `ebook-convert`; `brew install --cask calibre` |

**EPUB-only**: Calibre is not required for the final EPUB file; `ready` writes EPUB directly. **MOBI** always uses Calibre’s `ebook-convert` after an internal EPUB step.

## Folder convention (default)

Keep sources and outputs predictable:

| Role | Path |
|------|------|
| Source Markdown | `~/Desktop/md/<name>.md` |
| Kindle / export | `~/Desktop/md/kindle/<name>.mobi` or `.epub` |

Do not assume a different Desktop layout unless the user specifies one.

## Workflow

1. Save the Markdown file under **`~/Desktop/md/<name>.md`**.
2. Ensure the output directory exists: `mkdir -p ~/Desktop/md/kindle`.
3. Run **`ready`** with **explicit `-output`** so the MOBI/EPUB lands in `kindle/` (omitting `-output` places the file next to the input).

### MOBI (default format)

```bash
mkdir -p ~/Desktop/md/kindle
ready -input ~/Desktop/md/my-doc.md -output ~/Desktop/md/kindle/my-doc.mobi
```

### EPUB

```bash
mkdir -p ~/Desktop/md/kindle
ready -input ~/Desktop/md/my-doc.md -format epub -output ~/Desktop/md/kindle/my-doc.epub
```

### CLI reference

- **`-input`** — input `.md` file (required)
- **`-format`** — `mobi` or `epub` (default: `mobi`)
- **`-output`** — output path (recommended for `md/kindle/` layout)

## Email to Kindle

When the user wants the document delivered to their Kindle (the default when they ask to "send" something to Kindle), email the file via Apple Mail after converting.

- **Kindle address**: `adolfo.heriz.ocampo_QSaEKm@kindle.com`
- **Format must be EPUB.** Amazon's Send-to-Kindle email rejects `.mobi` attachments (dropped in 2022). Always convert with `-format epub` for this flow — Calibre is not needed.
- **Sender**: Mail.app sends from the user's account (`adolfo.heriz.ocampo@gmail.com`), which must be on Amazon's Approved Personal Document E-mail List.

### Workflow

1. Convert to EPUB into the usual layout:

   ```bash
   mkdir -p ~/Desktop/md/kindle
   ready -input ~/Desktop/md/my-doc.md -format epub -output ~/Desktop/md/kindle/my-doc.epub
   ```

2. Send it (substitute the real path and a subject, e.g. the document name):

   ```bash
   osascript <<'EOF'
   set epubFile to POSIX file "/Users/addehd/Desktop/md/kindle/my-doc.epub"
   tell application "Mail"
       set msg to make new outgoing message with properties {subject:"my-doc", visible:false}
       tell msg
           make new to recipient with properties {address:"adolfo.heriz.ocampo_QSaEKm@kindle.com"}
           make new attachment with properties {file name:epubFile} at after the last paragraph
       end tell
       delay 2
       send msg
   end tell
   EOF
   ```

   Keep the `delay 2` — sending immediately after adding an attachment can silently drop it.

### Email pitfalls

- **Automation permission prompt** — the first run from a given host app (Cursor, Terminal, …) triggers a macOS "wants to control Mail" dialog; the user must click OK once.
- **`send` is fire-and-forget** — success means queued, not delivered. If the document never arrives, check Mail's Outbox and that the sender is on Amazon's approved list.
- **MOBI attachment** — if a `.mobi` was emailed by mistake, Amazon bounces or silently drops it; re-send as EPUB.

## Pitfalls

- **`ready` not found** — build/install from the repo root (`./install.sh`) and confirm `~/bin` on PATH.
- **MOBI errors about `ebook-convert`** — install Calibre; MOBI conversion depends on it.
- **Wrong output location** — without `-output`, the default is beside the input file; use `-output ~/Desktop/md/kindle/...` for this workflow.
