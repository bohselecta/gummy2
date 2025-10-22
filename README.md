# CUIDADO

> *"Cuidado Llamas!!"* 🦙

A premium AI chat interface with custom llama branding. Built with Flask and Ollama, featuring elegant design and seamless local/remote access.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start Ollama
ollama serve

# Run CUIDADO
python3 premium_app.py
```

**Access**: http://localhost:5005

## Features

- **🎨 Premium Design**: Elegant button with micro-interactions
- **🦙 Custom Branding**: SVG logo and llama identity
- **💬 Dual Modes**: Conversation and Coder modes
- **🌐 Flexible Access**: Local + ngrok public tunneling
- **⚡ Live Status**: Public/Offline indicators

## Configuration

**ngrok Setup** (for public sharing):
```bash
export NGROK_AUTH_TOKEN="your_token"
ngrok http 5005
```

**Model Selection**:
Edit `premium_app.py`: `current_model = "gemma3:4b"`

## Architecture

- **Backend**: Flask + Ollama API
- **Frontend**: Vanilla JavaScript + custom styling
- **Assets**: Custom SVG logos and icons
- **Tunneling**: ngrok for secure public access

---

*"And now for something completely different..."* 🎭