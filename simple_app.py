#!/usr/bin/env python3
"""
Simple Ollama Web Host - Working Version
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

# Simple HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ollama Web Host</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .header { text-align: center; margin-bottom: 20px; }
        .mode-buttons { text-align: center; margin-bottom: 20px; }
        .mode-btn { padding: 10px 20px; margin: 0 10px; border: none; border-radius: 5px; cursor: pointer; }
        .mode-btn.active { background: #007bff; color: white; }
        .chat-area { height: 400px; border: 1px solid #ddd; padding: 10px; overflow-y: auto; margin-bottom: 20px; }
        .input-area { display: flex; gap: 10px; }
        .input-field { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .send-btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .message { margin-bottom: 10px; padding: 10px; border-radius: 5px; }
        .user-message { background: #e3f2fd; text-align: right; }
        .ai-message { background: #f5f5f5; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🦙 Ollama Web Host</h1>
            <p>Model: <strong id="current-model">{{ current_model }}</strong></p>
        </div>
        
        <div class="mode-buttons">
            <button class="mode-btn active" id="conversation-btn">💬 Conversation</button>
            <button class="mode-btn" id="coder-btn">💻 Coder</button>
        </div>
        
        <div class="chat-area" id="chat-area">
            <div class="message ai-message">
                <strong>AI:</strong> Hello! I'm ready to help. Choose between Conversation or Coder mode.
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" class="input-field" id="user-input" placeholder="Type your message here..." />
            <button class="send-btn" id="send-btn">Send</button>
        </div>
    </div>

    <script>
        console.log('Script loaded');
        
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
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        function setMode(mode) {
            console.log('Setting mode to:', mode);
            currentMode = mode;
            
            // Update button styles
            document.getElementById('conversation-btn').classList.toggle('active', mode === 'conversation');
            document.getElementById('coder-btn').classList.toggle('active', mode === 'coder');
            
            // Add message
            addMessage('ai', `Switched to ${mode} mode`);
        }
        
        function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            console.log('Sending message:', message);
            
            // Add user message
            addMessage('user', message);
            input.value = '';
            
            // Disable send button
            const sendBtn = document.getElementById('send-btn');
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';
            
            // Send to server
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.response) {
                    addMessage('ai', data.response);
                } else if (data.error) {
                    addMessage('ai', 'Error: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('ai', 'Connection error. Please check if Ollama is running.');
            })
            .finally(() => {
                sendBtn.disabled = false;
                sendBtn.textContent = 'Send';
            });
        }
        
        function addMessage(sender, content) {
            const chatArea = document.getElementById('chat-area');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            const senderText = sender === 'user' ? 'You' : 'AI';
            messageDiv.innerHTML = `<strong>${senderText}:</strong> ${content}`;
            
            chatArea.appendChild(messageDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }
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
        system_prompt = "You are an expert programmer. Provide clear, concise code examples with explanations."
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
    print("🦙 Ollama Web Host - Simple Version")
    print("=" * 60)
    
    local_ip = get_local_ip()
    print(f"🌐 Server starting on:")
    print(f"   Local:   http://localhost:5004")
    print(f"   Network: http://{local_ip}:5004")
    print("=" * 60)
    
    # Open browser after a short delay
    Timer(1.5, lambda: webbrowser.open(f'http://{local_ip}:5004')).start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5004, debug=False)
