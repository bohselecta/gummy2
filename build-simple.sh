#!/bin/bash

# Simple build script for Ollama Web Host Mac App
# This version doesn't require an icon file

echo "🚀 Building Ollama Web Host for macOS..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install --break-system-packages -q Flask requests pyinstaller || {
    echo "Trying without --break-system-packages flag..."
    pip3 install -q Flask requests pyinstaller
}

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist *.spec

# Build the app
echo "🔨 Building application bundle..."
pyinstaller --name="OllamaWebHost" \
    --windowed \
    --onefile \
    --hidden-import=flask \
    --hidden-import=requests \
    --osx-bundle-identifier=com.ollama.webhost \
    app.py

# Check if build was successful
if [ -d "dist/OllamaWebHost.app" ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "📱 Your app is ready at: dist/OllamaWebHost.app"
    echo ""
    echo "═══════════════════════════════════════════════════"
    echo "🎉 READY TO USE!"
    echo "═══════════════════════════════════════════════════"
    echo ""
    echo "📋 Quick Start:"
    echo "   1. Make sure Ollama is installed:"
    echo "      → Download from: https://ollama.ai"
    echo ""
    echo "   2. Pull at least one model:"
    echo "      → ollama pull llama3.2"
    echo "      → ollama pull deepseek-coder (for coding)"
    echo ""
    echo "   3. Double-click 'OllamaWebHost.app' to start!"
    echo ""
    echo "   4. Share the network URL shown in the terminal"
    echo "      with anyone on your local network"
    echo ""
    echo "═══════════════════════════════════════════════════"
    echo ""
else
    echo "❌ Build failed. Please check the error messages above."
    exit 1
fi
