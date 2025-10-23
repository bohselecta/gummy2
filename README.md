# CUIDADO

> *"Cuidado Llamas!!"* 🦙

A premium AI chat interface with custom llama branding. Built with Flask and Ollama, featuring elegant design, seamless local/remote access, and **collaborative multi-user rooms**.

## Quick Start

### Single-User Mode
```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama
ollama serve

# Run CUIDADO (single-user)
python3 premium_app.py
```
**Access**: http://localhost:5005

### Collaborative Mode
```bash
# Run CUIDADO Collaborative (multi-user)
python3 collaborative_app.py
```
**Access**: http://localhost:5006

## Features

### Single-User Mode
- **🎨 Premium Design**: Elegant button with micro-interactions
- **🦙 Custom Branding**: SVG logo and llama identity
- **💬 Dual Modes**: Conversation and Coder modes
- **🌐 Flexible Access**: Local + ngrok public tunneling
- **⚡ Live Status**: Public/Offline indicators

### Collaborative Mode
- **👥 Multi-User Rooms**: Share AI conversations with others
- **⚖️ Fair Queue**: Round-robin scheduling prevents resource hogging
- **📡 Live Streaming**: Real-time message streaming to all users
- **🔒 Thread Isolation**: Each user maintains private conversation context
- **👀 Live Mirrors**: See others' AI generations as they happen
- **📊 Queue Position**: Know your place in line with ETA estimates
- **⌨️ Typing Indicators**: See when others are composing messages
- **🎭 Friendly Names**: Auto-generated animal-themed nicknames

## Configuration

**ngrok Setup** (for public sharing):
```bash
export NGROK_AUTH_TOKEN="your_token"
ngrok http 5005  # Single-user
ngrok http 5006  # Collaborative
```

**Model Selection**:
Edit `premium_app.py` or `collaborative_app.py`: `current_model = "gemma3:4b"`

**Worker Scaling** (Collaborative):
```bash
export WORKERS=2  # Run 2 parallel workers (default: 1)
python3 collaborative_app.py
```

## Architecture

### Single-User Mode
- **Backend**: Flask + Ollama API
- **Frontend**: Vanilla JavaScript + custom styling
- **Assets**: Custom SVG logos and icons
- **Tunneling**: ngrok for secure public access

### Collaborative Mode
- **Backend**: FastAPI + WebSockets + Ollama streaming
- **Queue**: In-memory FIFO with round-robin fairness
- **State**: Per-room user/thread management
- **Streaming**: Real-time chunk broadcasting
- **Frontend**: Enhanced UI with multi-user awareness

## Usage Examples

### Creating a Collaborative Room
1. Visit http://localhost:5006
2. Click "Create Room" → Get room URL
3. Share URL with others
4. Everyone joins with optional nicknames
5. Chat collaboratively with fair queuing

### Room Features
- **Queue Position**: "⏳ 2nd in queue (~18s)"
- **Generation Banner**: "🤖 Generating for @alice..."
- **Thread Visibility**: Toggle between "My Chat" and "View Others"
- **Live Updates**: See all activity in real-time

---

*"And now for something completely different..."* 🎭