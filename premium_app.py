#!/usr/bin/env python3
"""
Ollama Web Host - Polished Version with Premium Styling
"""

import socket
import requests
import json
from flask import Flask, render_template_string, request, jsonify
import webbrowser
from threading import Timer

app = Flask(__name__)

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
current_model = "gemma3:4b"
current_mode = "conversation"

# Premium HTML Template with Glass Design
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CUIDADO</title>
    <style>
        :root {
            --bg: #0A0B10;
            --panel: #10131A;
            --glass: rgba(255,255,255,.05);
            --border: #232334;
            --text: #EAEAF0;
            --sub: #9AA0B3;
            --cherry: #FF4F77;
            --pink: #FF7AB6;
            --blue: #4D6BFE;
            --teal: #00E5A8;
            --ring: rgba(255,255,255,.22);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body {
            height: 100%;
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }
        
        /* Background glows */
        .bg-glow::before,
        .bg-glow::after {
            content: "";
            position: fixed;
            inset: auto;
            filter: blur(70px);
            pointer-events: none;
            z-index: -1;
            opacity: .35;
        }
        
        .bg-glow::before {
            top: -30vh;
            left: 10vw;
            width: 40vw;
            height: 40vh;
            background: radial-gradient(closest-side, var(--blue), transparent 70%);
        }
        
        .bg-glow::after {
            bottom: -30vh;
            right: -10vw;
            width: 45vw;
            height: 45vh;
            background: radial-gradient(closest-side, var(--pink), transparent 70%);
        }
        
        .container {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            position: relative;
        }
        
        /* Header */
        .header {
            position: sticky;
            top: 0;
            z-index: 20;
            background: rgba(0,0,0,.3);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255,255,255,.1);
            padding: 12px 20px;
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 20px;
            font-weight: 600;
            text-shadow: 0 0 12px rgba(255,79,119,.5);
        }
        
        .logo-img {
            height: 40px;
            width: auto;
            object-fit: contain;
        }
        
        .header-right {
            margin-left: auto;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .connection-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,.1);
            background: rgba(255,255,255,.05);
            padding: 6px 10px;
            font-size: 12px;
        }
        
        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #00E5A8;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .mode-selector {
            display: flex;
            gap: 4px;
            background: rgba(255,255,255,.05);
            padding: 4px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,.1);
        }
        
        .mode-btn {
            padding: 8px 16px;
            border: none;
            background: transparent;
            color: var(--sub);
            cursor: pointer;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s;
            font-size: 14px;
        }
        
        .mode-btn.active {
            background: rgba(255,255,255,.1);
            color: var(--text);
        }
        
        .mode-btn:hover:not(.active) {
            background: rgba(255,255,255,.05);
        }
        
        /* Chat area */
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
        }
        
        .message {
            margin-bottom: 20px;
            animation: fadeIn 0.15s ease both;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: none; }
        }
        
        .message.user {
            display: flex;
            justify-content: flex-end;
        }
        
        .message.assistant {
            display: flex;
            justify-content: flex-start;
        }
        
        .message-content {
            max-width: 80%;
            padding: 16px;
            border-radius: 16px;
            word-wrap: break-word;
            position: relative;
        }
        
        .message.user .message-content {
            background: linear-gradient(135deg, var(--cherry), var(--pink));
            color: white;
            box-shadow: 0 10px 40px rgba(255,79,119,.25);
        }
        
        .message.assistant .message-content {
            background: rgba(255,255,255,.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,.1);
            color: var(--text);
            box-shadow: 0 10px 60px rgba(0,0,0,.45);
        }
        
        .message-content pre {
            background: #0e1118;
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 12px;
            overflow-x: auto;
            margin: 8px 0;
        }
        
        .message-content code {
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
        }
        
        .message-content code:not(pre code) {
            background: #0e1118;
            border: 1px solid rgba(255,255,255,.1);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        .message-content h1,
        .message-content h2,
        .message-content h3 {
            letter-spacing: -0.01em;
            margin: 12px 0 8px 0;
        }
        
        .message-content p {
            margin: 8px 0;
        }
        
        .message-content a {
            color: #73A7FF;
            text-decoration: none;
            border-bottom: 1px dashed rgba(115,167,255,.2);
        }
        
        /* Loading indicator */
        .loading {
            display: flex;
            gap: 4px;
            padding: 12px;
        }
        
        .loading span {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: rgba(255,255,255,.7);
            animation: bounce 1.4s infinite ease-in-out both;
        }
        
        .loading span:nth-child(1) { animation-delay: -0.32s; }
        .loading span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        /* Input area */
        .input-container {
            position: sticky;
            bottom: 0;
            background: rgba(0,0,0,.3);
            backdrop-filter: blur(20px);
            border-top: 1px solid rgba(255,255,255,.1);
            padding: 12px 20px;
        }
        
        .input-wrapper {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: flex-end;
            gap: 12px;
        }
        
        .input-field {
            flex: 1;
            min-height: 44px;
            max-height: 180px;
            padding: 12px 16px;
            border: 1px solid var(--border);
            border-radius: 16px;
            background: #0e1118;
            color: var(--text);
            font-size: 15px;
            line-height: 1.6;
            resize: none;
            font-family: inherit;
            transition: all 0.3s;
        }
        
        .input-field:focus {
            outline: none;
            border-color: var(--ring);
            box-shadow: 0 0 0 2px var(--ring);
        }
        
        .input-field::placeholder {
            color: rgba(255,255,255,.4);
        }
        
        .send-btn {
            position: relative;
            width: 44px;
            height: 44px;
            border-radius: 16px;
            border: none;
            background: linear-gradient(135deg, #FF4F77, #FF6F91, #FF9CBB);
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            box-shadow: 0 0 25px rgba(255,79,119,.35);
            overflow: hidden;
        }
        
        .send-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 0 35px rgba(255,79,119,.6);
        }
        
        .send-btn:hover:not(:disabled)::before {
            opacity: 1;
        }
        
        .send-btn:active:not(:disabled) {
            transform: scale(0.95);
        }
        
        .send-btn::before {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: 16px;
            background: rgba(255,255,255,.1);
            backdrop-filter: blur(4px);
            opacity: 0;
            transition: opacity 0.2s ease;
        }
        
        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .send-btn img {
            position: relative;
            width: 20px;
            height: 20px;
            object-fit: contain;
            transition: transform 0.2s ease;
            z-index: 1;
        }
        
        .send-btn.loading img {
            display: none;
        }
        
        .send-btn.loading::after {
            content: '';
            position: absolute;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255,255,255,.7);
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            z-index: 1;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .header-content {
                padding: 0 16px;
            }
            
            .chat-container {
                padding: 16px;
            }
            
            .input-container {
                padding: 12px 16px;
            }
            
            .message-content {
                max-width: 90%;
            }
        }
        
        /* Error message */
        .error-message {
            background: rgba(255,79,119,.1);
            border: 1px solid rgba(255,79,119,.3);
            color: #ffb3c1;
            padding: 12px 16px;
            border-radius: 12px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container bg-glow">
        <div class="header">
            <div class="header-content">
                <div class="logo">
                    <img src="/cuidado-logo.svg" alt="CUIDADO" class="logo-img" />
                    <span>CUIDADO</span>
                </div>
                <div class="header-right">
                    <div class="connection-badge">
                        <div class="status-dot"></div>
                        <span id="connection-status">Local (Ollama)</span>
                    </div>
                    <div class="mode-selector">
                        <button class="mode-btn active" id="conversation-btn">Conversation</button>
                        <button class="mode-btn" id="coder-btn">Coder</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="chat-container" id="chat-container">
            <div class="message assistant">
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
                    placeholder="Ask anything…" 
                    rows="1"
                ></textarea>
                <button class="send-btn" id="send-btn">
                    <img src="/send-arrow.svg" alt="Send" class="send-arrow" />
                </button>
            </div>
        </div>
    </div>
    
    <script>
        console.log('CUIDADO loaded');
        
        let currentMode = 'conversation';
        
        // Mode buttons
        document.getElementById('conversation-btn').addEventListener('click', function() {
            setMode('conversation');
        });
        
        document.getElementById('coder-btn').addEventListener('click', function() {
            setMode('coder');
        });
        
        // Send button
        document.getElementById('send-btn').addEventListener('click', function() {
            sendMessage();
        });
        
        // Enter key
        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Auto-resize textarea
        const textarea = document.getElementById('user-input');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 180) + 'px';
        });
        
        function setMode(mode) {
            console.log('Setting mode to:', mode);
            currentMode = mode;
            
            // Update button styles
            document.getElementById('conversation-btn').classList.toggle('active', mode === 'conversation');
            document.getElementById('coder-btn').classList.toggle('active', mode === 'coder');
            
            // Add system message
            addMessage('assistant', `Switched to ${mode} mode`);
        }
        
        function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            console.log('Sending message:', message);
            
            // Add user message
            addMessage('user', message);
            input.value = '';
            input.style.height = 'auto';
            
            // Disable send button and show loading
            const sendBtn = document.getElementById('send-btn');
            sendBtn.disabled = true;
            sendBtn.classList.add('loading');
            addLoadingIndicator();
            
            // Send to server
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                removeLoadingIndicator();
                
                if (data.response) {
                    addMessage('assistant', data.response);
                } else if (data.error) {
                    addMessage('assistant', '❌ Error: ' + data.error);
                }
            })
            .catch(error => {
                removeLoadingIndicator();
                console.error('Error:', error);
                addMessage('assistant', '❌ Connection error. Please check if Ollama is running.');
            })
            .finally(() => {
                sendBtn.disabled = false;
                sendBtn.classList.remove('loading');
                input.focus();
            });
        }
        
        function addMessage(sender, content) {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            // Format code blocks
            const formattedContent = content.replace(/```([^`]+)```/g, (match, code) => {
                return `<pre><code>${escapeHtml(code.trim())}</code></pre>`;
            });
            
            contentDiv.innerHTML = formattedContent.replace(/\\n/g, '<br>');
            
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
        
        // Check if ngrok is active
        fetch('/ngrok-status')
            .then(response => response.json())
            .then(data => {
                const statusElement = document.getElementById('connection-status');
                const dotElement = document.querySelector('.status-dot');
                
                if (data.ngrok_active) {
                    statusElement.textContent = 'Public';
                    dotElement.style.background = '#00E5A8'; // Green
                } else {
                    statusElement.textContent = 'Offline';
                    dotElement.style.background = '#FF4F77'; // Red
                }
            })
            .catch(() => {
                // Set offline if error
                document.getElementById('connection-status').textContent = 'Offline';
                document.querySelector('.status-dot').style.background = '#FF4F77';
            });
    </script>
</body>
</html>
"""

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unable to determine"

@app.route('/')
def home():
    """Render the main chat interface"""
    return render_template_string(HTML_TEMPLATE, current_model=current_model)

@app.route('/send-arrow.svg')
def send_arrow():
    """Serve the custom send arrow SVG"""
    from flask import send_file
    return send_file('send-arrow.svg', mimetype='image/svg+xml')

@app.route('/cuidado-logo.svg')
def cuidado_logo():
    """Serve the CUIDADO logo SVG"""
    from flask import send_file
    return send_file('cuidado-logo.svg', mimetype='image/svg+xml')

@app.route('/cuidado-logo.png')
def logo():
    """Serve the CUIDADO logo"""
    from flask import send_file
    return send_file('cuidado-logo.png', mimetype='image/png')

@app.route('/ngrok-status')
def ngrok_status():
    """Check if ngrok is active"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=1)
        if response.status_code == 200:
            data = response.json()
            return jsonify({'ngrok_active': len(data.get('tunnels', [])) > 0})
    except:
        pass
    return jsonify({'ngrok_active': False})

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
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

if __name__ == '__main__':
    print("=" * 60)
    print("CUIDADO - Premium AI Chat Interface")
    print("=" * 60)
    
    local_ip = get_local_ip()
    print(f"🌐 Server starting on:")
    print(f"   Local:   http://localhost:5005")
    print(f"   Network: http://{local_ip}:5005")
    print("=" * 60)
    
    # Open browser after a short delay
    Timer(1.5, lambda: webbrowser.open(f'http://{local_ip}:5005')).start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5005, debug=False)
