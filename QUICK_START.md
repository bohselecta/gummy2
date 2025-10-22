# 🚀 QUICK START GUIDE

## Step 1: Prerequisites ✅

Before building, make sure you have:

- [ ] **Python 3.8+** installed
  - Check: `python3 --version`
  - Install: https://www.python.org/downloads/

- [ ] **Ollama** installed  
  - Check: `ollama --version`
  - Install: https://ollama.ai

- [ ] At least **one model** downloaded
  - Quick: `ollama pull llama3.2`

## Step 2: Build the App 🔨

```bash
# Make the build script executable (first time only)
chmod +x build-simple.sh

# Run the build script
./build-simple.sh
```

**Wait 1-2 minutes** while it installs dependencies and builds the app.

## Step 3: Find Your App 📱

Your app will be at: `dist/OllamaWebHost.app`

**To use it:**
1. Double-click `OllamaWebHost.app`
2. A browser opens automatically
3. Look at the terminal for your **network IP**
4. Share that IP with others: `http://192.168.x.x:5000`

## Step 4: Share with Your Team 🌐

Anyone on your **same WiFi network** can:
1. Open their browser
2. Go to `http://YOUR_IP:5000`
3. Start chatting with your local AI!

---

## Common Issues 🔧

**"Cannot connect to Ollama"**
```bash
# Make sure Ollama is running:
ollama serve
```

**"No models found"**
```bash
# Pull a model first:
ollama pull llama3.2
```

**Can't access from other devices**
- Make sure you're on the same WiFi
- Check your firewall settings
- Try disabling VPN

**App won't open on Mac**
- Right-click → Open (first time only)
- Or: System Preferences → Security → Allow

---

## What's Next? 🎯

1. **Try different models**
   ```bash
   ollama pull mistral        # Fast & efficient
   ollama pull deepseek-coder # Best for coding
   ollama pull llama3.2       # Great all-rounder
   ```

2. **Customize the app**
   - Edit `app.py` to change colors, models, or behavior
   - Rebuild with `./build-simple.sh`

3. **Invite your team**
   - Share your network IP
   - Everyone can use your AI simultaneously!

---

**Need help?** Check the full README.md or visit https://ollama.ai/docs

**Enjoying it?** Star the project and share with friends! ⭐
