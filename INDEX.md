# 🦙 OLLAMA WEB HOST - YOUR PROJECT INDEX

Welcome! This is your complete Ollama Web Host application. Here's where to start:

## 📂 PROJECT FILES

### 🚀 START HERE
- **[START_HERE.md](START_HERE.md)** - Complete overview and getting started guide
- **[QUICK_START.md](QUICK_START.md)** - Fast-track 3-step guide
- **[VISUAL_GUIDE.md](VISUAL_GUIDE.md)** - See how everything works visually

### 🛠️ BUILD & RUN
- **check-requirements.sh** - Run first! Checks if you have everything
- **build-simple.sh** - Build the Mac app (recommended)
- **build.sh** - Alternative build script

### 📱 THE APP
- **app.py** - Main application (Flask + HTML + Ollama integration)
- **requirements.txt** - Python dependencies

### 📖 DOCUMENTATION
- **README.md** - Full technical documentation
- **All the .md files** - Various helpful guides

---

## ⚡ QUICK START (30 seconds)

```bash
# 1. Check you have everything
./check-requirements.sh

# 2. Build the app  
./build-simple.sh

# 3. Double-click the app in dist/ folder!
```

That's it! Your app will be at: `dist/OllamaWebHost.app`

---

## 🎯 WHAT THIS APP DOES

**In simple terms:**
Takes your local Ollama installation and makes it accessible to anyone on your WiFi network through a beautiful chat interface.

**Key features:**
- ✅ Double-click to run (no installation)
- ✅ Beautiful web interface
- ✅ Two modes: Conversation & Coder
- ✅ Works on any device with a browser
- ✅ Completely private (stays on your network)
- ✅ No API keys or cloud services needed

---

## 📋 PREREQUISITES

Before building, you need:

1. **macOS** (this is a Mac app)
2. **Python 3.8+** → [Download](https://www.python.org/downloads/)
3. **Ollama** → [Download](https://ollama.ai)
4. **A model downloaded** → `ollama pull llama3.2`

Run `./check-requirements.sh` to verify!

---

## 🗂️ FILE GUIDE

### For Building the App
```
check-requirements.sh  → Verify prerequisites
build-simple.sh       → Build the Mac app
requirements.txt      → Python packages needed
```

### The Application
```
app.py               → Main Flask server + HTML interface
                       - Web server (Flask)
                       - Chat interface (HTML/JS)
                       - Ollama integration
                       - Model switching
```

### After Building
```
dist/
└── OllamaWebHost.app  → Your double-clickable Mac app!
```

### Documentation
```
START_HERE.md         → Best place to start
QUICK_START.md        → 3-step fast guide
VISUAL_GUIDE.md       → Diagrams and workflows
README.md             → Complete documentation
```

---

## 🎓 LEARNING PATH

**Never built a Mac app before?**
1. Read [START_HERE.md](START_HERE.md)
2. Run `./check-requirements.sh`
3. Read the output
4. Fix any issues
5. Run `./build-simple.sh`

**Want to understand how it works?**
1. Read [VISUAL_GUIDE.md](VISUAL_GUIDE.md)
2. Open `app.py` and read the comments
3. Check the Flask documentation

**Want to customize it?**
1. Edit `app.py` (it's well-commented)
2. Rebuild with `./build-simple.sh`
3. Test your changes

---

## 💡 COMMON WORKFLOWS

### First Time Setup
```bash
./check-requirements.sh
./build-simple.sh
# Double-click dist/OllamaWebHost.app
```

### Making Changes
```bash
# Edit app.py
nano app.py

# Rebuild
./build-simple.sh

# Test
# Double-click the new app
```

### Sharing with Team
```bash
# 1. Start the app (double-click)
# 2. Note the IP shown in terminal
# 3. Share: http://YOUR_IP:5000
# 4. Team members visit that URL
```

### Troubleshooting
```bash
# Check Ollama is running
ollama serve

# List models
ollama list

# Pull a model
ollama pull llama3.2

# Test the app directly
python3 app.py
```

---

## 🔍 WHICH FILE DO I NEED?

**I just want to build and use it:**
→ Run `./build-simple.sh`

**I want to understand it first:**
→ Read [START_HERE.md](START_HERE.md)

**I'm having issues:**
→ Run `./check-requirements.sh`

**I want to see diagrams:**
→ Read [VISUAL_GUIDE.md](VISUAL_GUIDE.md)

**I need detailed docs:**
→ Read [README.md](README.md)

**I want the fastest path:**
→ Read [QUICK_START.md](QUICK_START.md)

**I want to customize:**
→ Edit `app.py` (well-commented)

**I need help with Ollama:**
→ Visit [ollama.ai](https://ollama.ai)

---

## 🎯 WHAT TO DO RIGHT NOW

1. **If you haven't checked requirements:**
   ```bash
   ./check-requirements.sh
   ```

2. **If everything checks out:**
   ```bash
   ./build-simple.sh
   ```

3. **When build completes:**
   - Go to `dist/` folder
   - Double-click `OllamaWebHost.app`
   - Share the IP with your team!

---

## 📊 PROJECT STATS

- **Single Python file**: app.py (~500 lines, well-commented)
- **Zero dependencies** (once built)
- **One-click build**: ./build-simple.sh
- **Double-click to run**: No installation needed
- **Local network only**: Private and secure
- **Model agnostic**: Works with any Ollama model

---

## 🎨 CUSTOMIZATION QUICK REFERENCE

All in `app.py`:

**Change models:**
```python
DEFAULT_CODER_MODEL = "deepseek-coder"
DEFAULT_CONVERSATION_MODEL = "llama3.2"
```

**Change colors:**
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

**Change port:**
```python
app.run(host='0.0.0.0', port=5000)
```

**Change system prompt:**
```python
system_prompt = "Your custom instructions here"
```

Then rebuild: `./build-simple.sh`

---

## 🆘 NEED HELP?

**Python issues:**
- Make sure Python 3.8+ is installed
- Try: `python3 --version`

**Ollama issues:**
- Check: `ollama --version`
- Run: `ollama serve`

**Build issues:**
- Read the error message carefully
- Run: `./check-requirements.sh`
- Check you have disk space

**Runtime issues:**
- Test with: `python3 app.py`
- See actual error messages
- Check Ollama is running

**Still stuck?**
- Read the error messages
- Check [START_HERE.md](START_HERE.md)
- Try running `python3 app.py` to see detailed errors

---

## 🌟 WHAT MAKES THIS SPECIAL

Unlike other solutions:
- ✅ **No Docker** - Just Python
- ✅ **No config files** - Just run it
- ✅ **Single file** - Easy to understand
- ✅ **Double-clickable** - User friendly
- ✅ **Beautiful UI** - Modern design
- ✅ **Two modes** - Conversation & Coding
- ✅ **Auto-detects models** - Smart defaults
- ✅ **Network ready** - Share instantly

---

## 🚦 STATUS INDICATORS

When you run the app, you'll see:

**✅ Green dots** = Connected and working
**⚠️ Yellow warnings** = Non-critical issues
**❌ Red errors** = Fix these first

The terminal will show:
- Your local IP address
- Available models
- Connection status

---

## 📞 QUICK REFERENCE COMMANDS

```bash
# Check everything
./check-requirements.sh

# Build the app
./build-simple.sh

# Run directly (for testing)
python3 app.py

# List Ollama models
ollama list

# Pull a model
ollama pull llama3.2

# Start Ollama server
ollama serve

# Find your IP
ifconfig | grep "inet "
```

---

## 🎉 YOU'RE ALL SET!

Everything you need is in this folder. Start with:

```bash
./check-requirements.sh
```

Then if all good:

```bash
./build-simple.sh
```

Then enjoy your new app! 🎊

---

**Questions?** Read [START_HERE.md](START_HERE.md)

**Need details?** Read [README.md](README.md)

**Want to see diagrams?** Read [VISUAL_GUIDE.md](VISUAL_GUIDE.md)

**Just want to start?** Run `./build-simple.sh`

---

Made with ❤️ for the local AI community
