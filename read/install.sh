#!/usr/bin/env bash
set -e

# Build the Go binary
echo "Building ready binary..."
go build -o ready main.go

# Create ~/bin if it doesn't exist
mkdir -p ~/bin

# Move binary to ~/bin
echo "Installing ready to ~/bin..."
cp ready ~/bin/ready
chmod +x ~/bin/ready

echo "✓ Installation complete!"
echo ""
echo "Make sure ~/bin is in your PATH. Add this to your ~/.zshrc if needed:"
echo '  export PATH="$HOME/bin:$PATH"'
echo ""
echo "Usage: ready -input file.md [-output file.mobi] [-format mobi|epub]"
