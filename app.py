#!/usr/bin/env python3
"""
Ollama Web Host - Host your local Ollama installation with a simple web interface
"""

import socket
import requests
import json
from flask import Flask, render_template_string, request, jsonify, Response
import webbrowser
from threading import Timer

app = Flask(__name__)

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_CODER_MODEL = "deepseek-coder"
DEFAULT_CONVERSATION_MODEL = "llama3.2"

# Store current model and mode
current_model = DEFAULT_CONVERSATION_MODEL
current_mode = "conversation"

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ollama Web Host</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 900px;
            height: 90vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 24px;
            font-weight: 600;
        }
        
        .mode-selector {
            display: flex;
            gap: 10px;
            background: rgba(255,255,255,0.2);
            padding: 5px;
            border-radius: 10px;
        }
        
        .mode-btn {
            padding: 8px 16px;
            border: none;
            background: transparent;
            color: white;
            cursor: pointer;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .mode-btn.active {
            background: white;
            color: #667eea;
        }
        
        .mode-btn:hover:not(.active) {
            background: rgba(255,255,255,0.1);
        }
        
        .status-bar {
            background: #f8f9fa;
            padding: 12px 30px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #6c757d;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #28a745;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 30px;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 20px;
            display: flex;
            gap: 12px;
        }
        
        .message.user {
            flex-direction: row-reverse;
        }
        
        .message-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            flex-shrink: 0;
        }
        
        .message.user .message-avatar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .message.assistant .message-avatar {
            background: #e9ecef;
            color: #495057;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 12px;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .message.assistant .message-content {
            background: white;
            color: #212529;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .message-content pre {
            background: rgba(0,0,0,0.05);
            padding: 10px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 8px 0;
        }
        
        .message-content code {
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
        }
        
        .input-container {
            padding: 20px 30px;
            background: white;
            border-top: 1px solid #e9ecef;
        }
        
        .input-wrapper {
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }
        
        .input-field {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            font-size: 15px;
            resize: none;
            max-height: 120px;
            font-family: inherit;
            transition: border-color 0.3s;
        }
        
        .input-field:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .send-btn {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .send-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .send-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loading {
            display: flex;
            gap: 4px;
            padding: 12px;
        }
        
        .loading span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        
        .loading span:nth-child(1) { animation-delay: -0.32s; }
        .loading span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        .error-message {
            background: #dc3545;
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            margin: 10px 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🦙 Ollama Web Host</h1>
            <div class="mode-selector">
                <button class="mode-btn" id="conversation-btn" onclick="setMode('conversation')">💬 Conversation</button>
                <button class="mode-btn" id="coder-btn" onclick="setMode('coder')">💻 Coder</button>
            </div>
        </div>
        
        <div class="status-bar">
            <div class="status-indicator">
                <div class="status-dot"></div>
                <span id="status-text">Connected to Ollama</span>
            </div>
            <div style="font-size: 13px; color: #6c757d;">
                Model: <strong id="current-model">{{ current_model }}</strong>
            </div>
        </div>
        
        <div class="chat-container" id="chat-container">
            <div class="message assistant">
                <div class="message-avatar">AI</div>
                <div class="message-content">
                    <p>Hello! I'm ready to help. Choose between <strong>Conversation</strong> mode for general chat or <strong>Coder</strong> mode for programming assistance.</p>
                </div>
            </div>
        </div>
        
        <div class="input-container">
            <div class="input-wrapper">
                <textarea 
                    id="user-input" 
                    class="input-field" 
                    placeholder="Type your message here..." 
                    rows="1"
                    onkeydown="handleKeyPress(event)"
                ></textarea>
                <button class="send-btn" id="send-btn" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>
    
    <script>
        // Cache buster and debug
        console.log('JavaScript loaded at:', new Date().toISOString());
        console.log('setMode function defined:', typeof setMode);
        
        let currentMode = '{{ current_mode }}';
        
        // Initialize mode buttons
        updateModeButtons();
        
        function updateModeButtons() {
            console.log('updateModeButtons called');
            document.getElementById('conversation-btn').classList.toggle('active', currentMode === 'conversation');
            document.getElementById('coder-btn').classList.toggle('active', currentMode === 'coder');
        }
        
        async function setMode(mode) {
            console.log('setMode called with:', mode);
            try {
                const response = await fetch('/set_mode', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mode: mode })
                });
                
                const data = await response.json();
                if (data.success) {
                    currentMode = mode;
                    updateModeButtons();
                    document.getElementById('current-model').textContent = data.model;
                    
                    // Add system message
                    addMessage('assistant', `Switched to ${mode} mode (Model: ${data.model})`);
                }
            } catch (error) {
                console.error('Error setting mode:', error);
            }
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }
        
        function addMessage(role, content) {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = role === 'user' ? 'You' : 'AI';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            // Format code blocks
            const formattedContent = content.replace(/```([^`]+)```/g, (match, code) => {
                return `<pre><code>${escapeHtml(code.trim())}</code></pre>`;
            });
            
            contentDiv.innerHTML = formattedContent.replace(/\n/g, '<br>');
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(contentDiv);
            chatContainer.appendChild(messageDiv);
            
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function addLoadingIndicator() {
            const chatContainer = document.getElementById('chat-container');
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message assistant';
            loadingDiv.id = 'loading-indicator';
            
            loadingDiv.innerHTML = `
                <div class="message-avatar">AI</div>
                <div class="message-content">
                    <div class="loading">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
            
            chatContainer.appendChild(loadingDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function removeLoadingIndicator() {
            const loading = document.getElementById('loading-indicator');
            if (loading) loading.remove();
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function sendMessage() {
            console.log('sendMessage called');
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage('user', message);
            input.value = '';
            
            // Disable send button and show loading
            const sendBtn = document.getElementById('send-btn');
            sendBtn.disabled = true;
            addLoadingIndicator();
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                removeLoadingIndicator();
                
                if (data.response) {
                    addMessage('assistant', data.response);
                } else if (data.error) {
                    addMessage('assistant', '❌ Error: ' + data.error);
                }
            } catch (error) {
                removeLoadingIndicator();
                addMessage('assistant', '❌ Connection error. Please check if Ollama is running.');
                console.error('Error:', error);
            } finally {
                sendBtn.disabled = false;
                input.focus();
            }
        }
        
        // Auto-resize textarea
        const textarea = document.getElementById('user-input');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    </script>
</body>
</html>
"""

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unable to determine"

def check_ollama_connection():
    """Check if Ollama is running"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_available_models():
    """Get list of available models from Ollama"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
        return []
    except:
        return []

@app.route('/')
def home():
    """Render the main chat interface"""
    return render_template_string(HTML_TEMPLATE, 
                                 current_model=current_model,
                                 current_mode=current_mode)

@app.route('/test')
def test():
    """Test page to verify JavaScript works"""
    with open('test.html', 'r') as f:
        return f.read()

@app.route('/set_mode', methods=['POST'])
def set_mode():
    """Switch between coder and conversation modes"""
    global current_model, current_mode
    
    data = request.get_json()
    mode = data.get('mode', 'conversation')
    
    # Get available models
    available_models = get_available_models()
    
    if mode == 'coder':
        # Try to find a coder model
        for model_name in available_models:
            if 'coder' in model_name.lower() or 'code' in model_name.lower():
                current_model = model_name
                break
        else:
            # Default to first available model if no coder model found
            current_model = available_models[0] if available_models else DEFAULT_CODER_MODEL
        current_mode = 'coder'
    else:
        # Try to find a conversation model
        for model_name in available_models:
            if 'llama' in model_name.lower() or 'mistral' in model_name.lower():
                current_model = model_name
                break
        else:
            # Default to first available model
            current_model = available_models[0] if available_models else DEFAULT_CONVERSATION_MODEL
        current_mode = 'conversation'
    
    return jsonify({
        'success': True,
        'mode': current_mode,
        'model': current_model
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages and communicate with Ollama"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Prepare system prompt based on mode
    system_prompt = ""
    if current_mode == 'coder':
        system_prompt = "You are an expert programmer. Provide clear, concise code examples with explanations. Format code using markdown code blocks."
    else:
        system_prompt = "You are a helpful, friendly assistant. Provide clear and concise responses."
    
    try:
        # Send request to Ollama
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": current_model,
                "prompt": user_message,
                "system": system_prompt,
                "stream": False
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({'response': result.get('response', 'No response from model')})
        else:
            return jsonify({'error': f'Ollama error: {response.status_code}'}), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout. The model might be too large or slow.'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Cannot connect to Ollama. Make sure it is running.'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def open_browser():
    """Open the default browser to the app"""
    local_ip = get_local_ip()
    webbrowser.open(f'http://{local_ip}:5003')

if __name__ == '__main__':
    print("=" * 60)
    print("🦙 Ollama Web Host")
    print("=" * 60)
    
    # Check Ollama connection
    if check_ollama_connection():
        print("✅ Connected to Ollama")
        
        # Get available models
        models = get_available_models()
        if models:
            print(f"📦 Available models: {', '.join(models)}")
            # Set default model to first available
            current_model = models[0]
        else:
            print("⚠️  No models found. Please pull a model first:")
            print("   ollama pull llama3.2")
    else:
        print("❌ Cannot connect to Ollama!")
        print("   Make sure Ollama is running:")
        print("   1. Install Ollama from https://ollama.ai")
        print("   2. Run: ollama serve")
    
    print()
    local_ip = get_local_ip()
    print(f"🌐 Server starting on:")
    print(f"   Local:   http://localhost:5003")
    print(f"   Network: http://{local_ip}:5003")
    print()
    print("📱 Share the Network URL with anyone on your local network!")
    print("=" * 60)
    
    # Open browser after a short delay
    Timer(1.5, open_browser).start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5003, debug=False)
