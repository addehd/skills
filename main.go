package main

import (
	"bytes"
	"flag"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/alecthomas/chroma/formatters/html"
	"github.com/bmaupin/go-epub"
	"github.com/yuin/goldmark"
	highlighting "github.com/yuin/goldmark-highlighting"
	"github.com/yuin/goldmark/extension"
	"github.com/yuin/goldmark/parser"
	goldhtmlrenderer "github.com/yuin/goldmark/renderer/html"
)

func main() {
	var inputFile = flag.String("input", "", "Input markdown file")
	var outputFile = flag.String("output", "", "Output file (defaults to .mobi for Kindle)")
	var format = flag.String("format", "mobi", "Output format: epub or mobi (default: mobi for Kindle)")
	flag.Parse()

	if *inputFile == "" {
		log.Fatal("Please specify an input markdown file with -input flag")
	}

	// Normalize format
	*format = strings.ToLower(*format)
	if *format != "epub" && *format != "mobi" {
		log.Fatal("Format must be either 'epub' or 'mobi'")
	}

	if *outputFile == "" {
		*outputFile = strings.TrimSuffix(*inputFile, filepath.Ext(*inputFile)) + "." + *format
	}

	// Always create EPUB first
	epubFile := *outputFile
	if *format == "mobi" {
		epubFile = strings.TrimSuffix(*inputFile, filepath.Ext(*inputFile)) + ".epub"
	}

	if err := convertMarkdownToEPUB(*inputFile, epubFile); err != nil {
		log.Fatalf("Error converting markdown to EPUB: %v", err)
	}

	fmt.Printf("Successfully converted %s to %s\n", *inputFile, epubFile)

	// If MOBI format requested, convert EPUB to MOBI
	if *format == "mobi" {
		if err := convertEPUBToMOBI(epubFile, *outputFile); err != nil {
			log.Fatalf("Error converting EPUB to MOBI: %v", err)
		}
		fmt.Printf("Successfully converted %s to %s (Kindle-compatible)\n", epubFile, *outputFile)
		
		// Clean up temporary EPUB file
		if err := os.Remove(epubFile); err != nil {
			log.Printf("Warning: Could not remove temporary EPUB file: %v", err)
		}
	}
}

func convertMarkdownToEPUB(inputFile, outputFile string) error {
	// Read markdown file
	markdownContent, err := os.ReadFile(inputFile)
	if err != nil {
		return fmt.Errorf("failed to read markdown file: %w", err)
	}

	// Configure goldmark with syntax highlighting
	md := goldmark.New(
		goldmark.WithExtensions(
			extension.GFM,
			highlighting.NewHighlighting(
				highlighting.WithStyle("github"),
				highlighting.WithFormatOptions(
					html.WithClasses(true),
				),
			),
		),
		goldmark.WithParserOptions(
			parser.WithAutoHeadingID(),
		),
	goldmark.WithRendererOptions(
		goldhtmlrenderer.WithHardWraps(),
		goldhtmlrenderer.WithXHTML(),
	),
	)

	// Convert markdown to HTML
	var buf bytes.Buffer
	if err := md.Convert(markdownContent, &buf); err != nil {
		return fmt.Errorf("failed to convert markdown to HTML: %w", err)
	}

	// Create EPUB
	e := epub.NewEpub(filepath.Base(strings.TrimSuffix(inputFile, filepath.Ext(inputFile))))

	// Set metadata
	e.SetAuthor("Markdown to EPUB Converter")
	e.SetDescription("Converted from markdown file: " + inputFile)

	// Add CSS for syntax highlighting and code formatting
	// Create a temporary CSS file
	tmpDir := os.TempDir()
	tmpCSSFile := filepath.Join(tmpDir, "epub-styles.css")
	if err := os.WriteFile(tmpCSSFile, []byte(getCodeCSS()), 0644); err != nil {
		return fmt.Errorf("failed to write temporary CSS file: %w", err)
	}
	defer os.Remove(tmpCSSFile)

	cssPath, err := e.AddCSS(tmpCSSFile, "styles.css")
	if err != nil {
		return fmt.Errorf("failed to add CSS: %w", err)
	}

	// Add content as a section (go-epub will wrap it in proper HTML structure)
	_, err = e.AddSection(buf.String(), "content.xhtml", "", cssPath)
	if err != nil {
		return fmt.Errorf("failed to add content section: %w", err)
	}

	// Write EPUB file
	err = e.Write(outputFile)
	if err != nil {
		return fmt.Errorf("failed to write EPUB file: %w", err)
	}

	return nil
}

func convertEPUBToMOBI(epubFile, mobiFile string) error {
	// Check if ebook-convert is available
	if _, err := exec.LookPath("ebook-convert"); err != nil {
		return fmt.Errorf("ebook-convert not found. Please install Calibre: brew install --cask calibre")
	}

	// Convert EPUB to MOBI using Calibre's ebook-convert
	cmd := exec.Command("ebook-convert", epubFile, mobiFile)
	output, err := cmd.CombinedOutput()
	if err != nil {
		return fmt.Errorf("failed to convert EPUB to MOBI: %w\nOutput: %s", err, string(output))
	}

	return nil
}

func getCodeCSS() string {
	// CSS for syntax highlighting (GitHub style) and proper code formatting
	css := `
/* GitHub-style syntax highlighting */
.highlight { background: #f8f8f8; }
.chroma .err { color: #a61717; background-color: #e3d2d2; }
.chroma .k { color: #000000; font-weight: bold; }
.chroma .ch { color: #111111; font-style: normal; }
.chroma .cm { color: #111111; font-style: normal; }
.chroma .cp { color: #111111; font-weight: normal; }
.chroma .cpf { color: #111111; font-weight: normal; font-style: normal; }
.chroma .c1 { color: #111111; font-style: normal; }
.chroma .cs { color: #111111; font-weight: normal; font-style: normal; }
.chroma .gd { color: #000000; background-color: #ffdddd; }
.chroma .ge { color: #000000; font-style: italic; }
.chroma .gr { color: #aa0000; }
.chroma .gh { color: #999999; }
.chroma .gi { color: #000000; background-color: #ddffdd; }
.chroma .go { color: #888888; }
.chroma .gp { color: #555555; }
.chroma .gs { font-weight: bold; }
.chroma .gu { color: #aaaaaa; }
.chroma .gt { color: #aa0000; }
.chroma .kc { color: #000000; font-weight: bold; }
.chroma .kd { color: #000000; font-weight: bold; }
.chroma .kn { color: #000000; font-weight: bold; }
.chroma .kp { color: #000000; font-weight: bold; }
.chroma .kr { color: #000000; font-weight: bold; }
.chroma .kt { color: #445588; font-weight: bold; }
.chroma .m { color: #009999; }
.chroma .s { color: #d14; }
.chroma .na { color: #008080; }
.chroma .nb { color: #0086b3; }
.chroma .nc { color: #445588; font-weight: bold; }
.chroma .no { color: #008080; }
.chroma .nd { color: #3c5d5d; font-weight: bold; }
.chroma .ni { color: #800080; }
.chroma .ne { color: #990000; font-weight: bold; }
.chroma .nf { color: #990000; font-weight: bold; }
.chroma .nl { color: #990000; font-weight: bold; }
.chroma .nn { color: #555555; }
.chroma .nt { color: #000080; }
.chroma .nv { color: #008080; }
.chroma .ow { color: #000000; font-weight: bold; }
.chroma .w { color: #bbbbbb; }
.chroma .mb { color: #009999; }
.chroma .mf { color: #009999; }
.chroma .mh { color: #009999; }
.chroma .mi { color: #009999; }
.chroma .mo { color: #009999; }
.chroma .sa { color: #d14; }
.chroma .sb { color: #d14; }
.chroma .sc { color: #d14; }
.chroma .dl { color: #d14; }
.chroma .sd { color: #d14; }
.chroma .s2 { color: #d14; }
.chroma .se { color: #d14; }
.chroma .sh { color: #d14; }
.chroma .si { color: #d14; }
.chroma .sx { color: #d14; }
.chroma .sr { color: #009926; }
.chroma .s1 { color: #d14; }
.chroma .ss { color: #990073; }
.chroma .bp { color: #999999; }
.chroma .fm { color: #990000; font-weight: bold; }
.chroma .vc { color: #008080; }
.chroma .vg { color: #008080; }
.chroma .vi { color: #008080; }
.chroma .vm { color: #008080; }
.chroma .il { color: #009999; }

/* Code block styling */
pre {
    background-color: #f8f8f8;
    border: 1px solid #e1e4e8;
    border-radius: 6px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 12px;
    line-height: 1.45;
    overflow: auto;
    padding: 16px;
    margin: 16px 0;
}

code {
    background-color: rgba(27, 31, 35, 0.05);
    border-radius: 3px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 85%;
    margin: 0;
    padding: 0.2em 0.4em;
}

pre code {
    background-color: transparent;
    border-radius: 0;
    display: block;
    font-size: 100%;
    line-height: inherit;
    overflow: visible;
    padding: 0;
}

/* General styling */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.6;
    margin: 20px;
}

h1, h2, h3, h4, h5, h6 {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
}

p {
    margin-bottom: 16px;
}
`
	return css
}
