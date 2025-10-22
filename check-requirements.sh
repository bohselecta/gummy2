#!/bin/bash

# Pre-flight check script for Ollama Web Host
# Verifies all requirements are met before building

echo "🔍 Ollama Web Host - Pre-flight Check"
echo "═══════════════════════════════════════════════════"
echo ""

# Initialize counters
checks_passed=0
checks_failed=0

# Check 1: macOS
echo -n "1. Checking operating system... "
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ macOS detected"
    ((checks_passed++))
else
    echo "⚠️  Not macOS (detected: $OSTYPE)"
    echo "   This app is designed for macOS. It may work but is untested."
    ((checks_failed++))
fi

# Check 2: Python 3
echo -n "2. Checking Python 3... "
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version | awk '{print $2}')
    echo "✅ Found Python $python_version"
    ((checks_passed++))
else
    echo "❌ Python 3 not found"
    echo "   Install from: https://www.python.org/downloads/"
    ((checks_failed++))
fi

# Check 3: pip
echo -n "3. Checking pip... "
if command -v pip3 &> /dev/null; then
    pip_version=$(pip3 --version | awk '{print $2}')
    echo "✅ Found pip $pip_version"
    ((checks_passed++))
else
    echo "❌ pip3 not found"
    echo "   Usually comes with Python. Try reinstalling Python."
    ((checks_failed++))
fi

# Check 4: Ollama
echo -n "4. Checking Ollama installation... "
if command -v ollama &> /dev/null; then
    ollama_version=$(ollama --version | head -n 1)
    echo "✅ Found Ollama $ollama_version"
    ((checks_passed++))
else
    echo "❌ Ollama not found"
    echo "   Install from: https://ollama.ai"
    ((checks_failed++))
fi

# Check 5: Ollama running
echo -n "5. Checking if Ollama is running... "
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is running"
    ((checks_passed++))
else
    echo "⚠️  Ollama is not running"
    echo "   Start it with: ollama serve"
    echo "   (Or it may start automatically when you run the app)"
    # Don't count as failed - it's okay if not running yet
fi

# Check 6: Available models
echo -n "6. Checking for downloaded models... "
if command -v ollama &> /dev/null; then
    models=$(ollama list 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')
    if [ "$models" -gt 0 ]; then
        echo "✅ Found $models model(s)"
        echo "   Models available:"
        ollama list 2>/dev/null | tail -n +2 | awk '{print "      - " $1}'
        ((checks_passed++))
    else
        echo "⚠️  No models found"
        echo "   Download at least one model:"
        echo "      ollama pull llama3.2"
        echo "      ollama pull deepseek-coder"
    fi
else
    echo "⚠️  Cannot check (Ollama not installed)"
fi

# Check 7: Build directory writable
echo -n "7. Checking write permissions... "
if [ -w . ]; then
    echo "✅ Can write to current directory"
    ((checks_passed++))
else
    echo "❌ Cannot write to current directory"
    echo "   Check folder permissions"
    ((checks_failed++))
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "📊 Results: $checks_passed passed, $checks_failed critical issues"
echo "═══════════════════════════════════════════════════"
echo ""

if [ $checks_failed -eq 0 ]; then
    echo "🎉 All critical checks passed!"
    echo ""
    echo "You're ready to build. Run:"
    echo "   ./build-simple.sh"
    echo ""
    exit 0
else
    echo "⚠️  Please fix the issues above before building."
    echo ""
    echo "Need help? Check the README.md or QUICK_START.md"
    echo ""
    exit 1
fi
