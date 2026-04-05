# ready

A CLI tool that converts Markdown files to EPUB or MOBI (Kindle) format, with syntax highlighting for code blocks.

## Install

```bash
./install.sh
```

This builds the binary and installs it to `~/bin`. Make sure `~/bin` is in your PATH:

```bash
export PATH="$HOME/bin:$PATH"
```

### Requirements

- Go 1.21+
- [Calibre](https://calibre-ebook.com/) (only needed for MOBI output): `brew install --cask calibre`

## Usage

```bash
# Convert to MOBI (default, Kindle-compatible)
ready -input document.md

# Convert to EPUB
ready -input document.md -format epub

# Custom output path
ready -input document.md -output my-book.mobi
```

### Flags

- `-input` — Input Markdown file (required)
- `-output` — Output file path (defaults to input name with `.mobi` or `.epub` extension)
- `-format` — Output format: `mobi` or `epub` (default: `mobi`)
