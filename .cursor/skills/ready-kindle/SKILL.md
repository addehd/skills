---
name: ready-kindle
description: >-
  Converts Markdown to Kindle MOBI or EPUB using the `ready` CLI from this
  repository (`install.sh`, `main.go`), with a fixed layout under
  `~/Desktop/md/` and `~/Desktop/md/kindle/`. Use when the user wants
  Kindle-compatible output, MOBI/EPUB from Markdown, mentions `ready`,
  Calibre, or Desktop md/kindle folders.
---

# Markdown to Kindle via `ready`

This Skill file lives in the **`read` repository** next to `main.go` and `install.sh`. Build and install from that root.

## When to use

- Converting Markdown to **MOBI** (Kindle) or **EPUB**
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

## Pitfalls

- **`ready` not found** — build/install from the repo root (`./install.sh`) and confirm `~/bin` on PATH.
- **MOBI errors about `ebook-convert`** — install Calibre; MOBI conversion depends on it.
- **Wrong output location** — without `-output`, the default is beside the input file; use `-output ~/Desktop/md/kindle/...` for this workflow.
