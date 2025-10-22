#!/bin/bash

# Build script for Ollama Web Host Mac App

echo "🚀 Building Ollama Web Host for macOS..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  This script is designed for macOS. You may need to adjust it for your platform."
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install --break-system-packages -r requirements.txt

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist *.spec

# Build the app
echo "🔨 Building application bundle..."
pyinstaller --name="Ollama Web Host" \
    --windowed \
    --onefile \
    --icon=icon.icns \
    --add-data="app.py:." \
    --hidden-import=flask \
    --hidden-import=requests \
    --osx-bundle-identifier=com.ollama.webhost \
    app.py

# Check if build was successful
if [ -d "dist/Ollama Web Host.app" ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "📱 Your app is ready at: dist/Ollama Web Host.app"
    echo ""
    echo "To use it:"
    echo "1. Make sure Ollama is installed and running"
    echo "2. Double-click 'Ollama Web Host.app'"
    echo "3. Share the network URL with others!"
    echo ""
else
    echo "❌ Build failed. Please check the error messages above."
    exit 1
fi
