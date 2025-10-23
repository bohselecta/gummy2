// CUIDADO Collaborative - WebSocket Client Logic
// Handles multi-user chat with real-time streaming and queue management

class CollaborativeApp {
    constructor() {
        this.roomId = window.ROOM_ID;
        this.userId = null;
        this.threadId = null;
        this.nickname = null;
        this.websocket = null;
        this.currentMode = 'conversation';
        this.isConnected = false;
        this.typingTimeout = null;
        this.otherThreads = new Map(); // threadId -> {user, messages, isGenerating}
        this.showOthers = false;
        
        console.log('CollaborativeApp initialized with room ID:', this.roomId);
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.showNicknameModal();
    }
    
    setupEventListeners() {
        // Nickname modal
        document.getElementById('nickname-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.joinRoom();
            }
        });
        
        document.getElementById('join-btn').addEventListener('click', () => {
            this.joinRoom();
        });
        
        // Mode buttons
        document.getElementById('conversation-btn').addEventListener('click', () => {
            this.setMode('conversation');
        });
        
        document.getElementById('coder-btn').addEventListener('click', () => {
            this.setMode('coder');
        });
        
        // Send button
        document.getElementById('send-btn').addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Enter key
        document.getElementById('user-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        const textarea = document.getElementById('user-input');
        textarea.addEventListener('input', () => {
            this.handleTyping();
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 180) + 'px';
        });
        
        // Thread tabs
        document.getElementById('my-thread-tab').addEventListener('click', () => {
            this.showMyThread();
        });
        
        document.getElementById('others-thread-tab').addEventListener('click', () => {
            this.showOthersView();
        });
        
        document.getElementById('close-others').addEventListener('click', () => {
            this.hideOthersView();
        });
        
        // Copy room button
        document.getElementById('copy-room').addEventListener('click', () => {
            this.copyRoomUrl();
        });
    }
    
    showNicknameModal() {
        document.getElementById('nickname-modal').style.display = 'flex';
        document.getElementById('nickname-input').focus();
    }
    
    hideNicknameModal() {
        document.getElementById('nickname-modal').style.display = 'none';
        document.getElementById('main-app').classList.remove('hidden');
    }
    
    joinRoom() {
        const nickname = document.getElementById('nickname-input').value.trim();
        this.nickname = nickname || null;
        
        console.log('Joining room with nickname:', this.nickname);
        
        this.hideNicknameModal();
        this.connectWebSocket();
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.roomId}`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.updateConnectionStatus('Connected');
            
            // Send join message
            const joinMessage = {
                type: 'join',
                nickname: this.nickname
            };
            console.log('Sending join message:', joinMessage);
            this.websocket.send(JSON.stringify(joinMessage));
        };
        
        this.websocket.onmessage = (event) => {
            console.log('WebSocket message received:', event.data);
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.updateConnectionStatus('Disconnected');
            this.disableInput();
            
            // Attempt to reconnect after 3 seconds
            setTimeout(() => {
                if (!this.isConnected) {
                    this.connectWebSocket();
                }
            }, 3000);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('Error');
        };
    }
    
    handleWebSocketMessage(message) {
        console.log('Handling WebSocket message:', message);
        switch (message.type) {
            case 'joined':
                this.userId = message.user_id;
                this.threadId = message.thread_id;
                this.nickname = message.nickname;
                this.updateMyNickname();
                this.enableInput();
                break;
                
            case 'user_joined':
                this.updateUserCount();
                this.addSystemMessage(`${message.nickname} joined the room`);
                break;
                
            case 'user_left':
                this.updateUserCount();
                break;
                
            case 'enqueued':
                this.showQueuePosition(message.position, message.eta_seconds);
                break;
                
            case 'generation_start':
                this.showGenerationBanner(message.nickname);
                this.startTypingIndicator(message.thread_id, message.user_id, message.nickname);
                break;
                
            case 'chunk':
                this.handleChunk(message.thread_id, message.user_id, message.delta);
                break;
                
            case 'generation_done':
                this.hideGenerationBanner();
                this.stopTypingIndicator(message.thread_id, message.user_id);
                this.hideQueuePosition();
                break;
                
            case 'message_added':
                this.addMessageToThread(message.thread_id, message.user_id, message.content, message.nickname, 'user');
                break;
                
            case 'typing':
                this.handleTypingIndicator(message.user_id, message.thread_id, message.is_typing, message.nickname);
                break;
                
            case 'error':
                this.addSystemMessage(`Error: ${message.message}`);
                break;
        }
    }
    
    sendMessage() {
        const input = document.getElementById('user-input');
        const message = input.value.trim();
        
        if (!message || !this.isConnected) return;
        
        // Add user message to UI immediately
        this.addMessageToThread(this.threadId, this.userId, message, this.nickname, 'user');
        
        // Clear input
        input.value = '';
        input.style.height = 'auto';
        
        // Send to server
        this.websocket.send(JSON.stringify({
            type: 'message',
            thread_id: this.threadId,
            content: message
        }));
        
        // Show loading state
        this.showLoadingIndicator();
    }
    
    handleChunk(threadId, userId, delta) {
        if (threadId === this.threadId) {
            // My thread - append to current assistant message
            this.appendToCurrentMessage(delta);
        } else {
            // Other thread - update other thread display
            this.updateOtherThreadChunk(threadId, userId, delta);
        }
    }
    
    appendToCurrentMessage(delta) {
        const messagesContainer = document.getElementById('my-messages');
        let currentMessage = messagesContainer.querySelector('.message.assistant:last-child');
        
        if (!currentMessage || currentMessage.querySelector('.loading')) {
            // Create new assistant message
            currentMessage = this.createMessageElement('assistant', '');
            messagesContainer.appendChild(currentMessage);
        }
        
        const contentDiv = currentMessage.querySelector('.message-content');
        contentDiv.innerHTML += this.escapeHtml(delta);
        
        // Remove loading indicator if present
        const loading = messagesContainer.querySelector('.loading');
        if (loading) {
            loading.remove();
        }
        
        this.scrollToBottom();
    }
    
    updateOtherThreadChunk(threadId, userId, delta) {
        if (!this.otherThreads.has(threadId)) {
            this.otherThreads.set(threadId, {
                user: userId,
                nickname: this.getNicknameForUser(userId),
                messages: [],
                isGenerating: true
            });
        }
        
        const thread = this.otherThreads.get(threadId);
        thread.isGenerating = true;
        
        // Update UI if others view is open
        if (this.showOthers) {
            this.updateOthersDisplay();
        }
    }
    
    addMessageToThread(threadId, userId, content, nickname, role) {
        if (threadId === this.threadId) {
            // My thread
            this.addMessage(role, content);
        } else {
            // Other thread
            if (!this.otherThreads.has(threadId)) {
                this.otherThreads.set(threadId, {
                    user: userId,
                    nickname: nickname,
                    messages: [],
                    isGenerating: false
                });
            }
            
            const thread = this.otherThreads.get(threadId);
            thread.messages.push({ role, content, timestamp: Date.now() });
            thread.isGenerating = false;
            
            // Update UI if others view is open
            if (this.showOthers) {
                this.updateOthersDisplay();
            }
        }
    }
    
    addMessage(sender, content) {
        const messagesContainer = document.getElementById('my-messages');
        const messageDiv = this.createMessageElement(sender, content);
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    createMessageElement(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Format code blocks
        const formattedContent = content.replace(/```([^`]+)```/g, (match, code) => {
            return `<pre><code>${this.escapeHtml(code.trim())}</code></pre>`;
        });
        
        contentDiv.innerHTML = formattedContent.replace(/\n/g, '<br>');
        
        messageDiv.appendChild(contentDiv);
        return messageDiv;
    }
    
    addSystemMessage(content) {
        const messagesContainer = document.getElementById('my-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system';
        messageDiv.style.textAlign = 'center';
        messageDiv.style.margin = '10px 0';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.style.background = 'rgba(255,255,255,.03)';
        contentDiv.style.border = '1px solid rgba(255,255,255,.1)';
        contentDiv.style.fontSize = '12px';
        contentDiv.style.color = 'var(--sub)';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showLoadingIndicator() {
        const messagesContainer = document.getElementById('my-messages');
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
        
        messagesContainer.appendChild(loadingDiv);
        this.scrollToBottom();
    }
    
    showQueuePosition(position, etaSeconds) {
        const queuePill = document.getElementById('queue-pill');
        const queueText = document.getElementById('queue-text');
        
        queueText.textContent = `⏳ ${position}${this.getOrdinal(position)} in queue (~${etaSeconds}s)`;
        queuePill.classList.remove('hidden');
    }
    
    hideQueuePosition() {
        document.getElementById('queue-pill').classList.add('hidden');
    }
    
    showGenerationBanner(nickname) {
        const banner = document.getElementById('generation-banner');
        const text = document.getElementById('generation-text');
        
        text.textContent = `🤖 Generating for ${nickname}...`;
        banner.classList.remove('hidden');
    }
    
    hideGenerationBanner() {
        document.getElementById('generation-banner').classList.add('hidden');
    }
    
    startTypingIndicator(threadId, userId, nickname) {
        if (threadId === this.threadId) {
            // Show typing indicator in my thread
            this.showTypingIndicator(nickname);
        }
    }
    
    stopTypingIndicator(threadId, userId) {
        if (threadId === this.threadId) {
            this.hideTypingIndicator();
        }
    }
    
    showTypingIndicator(nickname) {
        const messagesContainer = document.getElementById('my-messages');
        let typingDiv = document.getElementById('typing-indicator');
        
        if (!typingDiv) {
            typingDiv = document.createElement('div');
            typingDiv.id = 'typing-indicator';
            typingDiv.className = 'typing-indicator';
            messagesContainer.appendChild(typingDiv);
        }
        
        typingDiv.innerHTML = `
            <span>${nickname} is typing</span>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingDiv = document.getElementById('typing-indicator');
        if (typingDiv) {
            typingDiv.remove();
        }
    }
    
    handleTypingIndicator(userId, threadId, isTyping, nickname) {
        // Handle typing indicators from other users
        // This could be enhanced to show typing indicators in the others view
    }
    
    handleTyping() {
        if (!this.isConnected) return;
        
        // Clear existing timeout
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }
        
        // Send typing start
        this.websocket.send(JSON.stringify({
            type: 'typing',
            thread_id: this.threadId,
            is_typing: true
        }));
        
        // Send typing stop after 1 second of inactivity
        this.typingTimeout = setTimeout(() => {
            this.websocket.send(JSON.stringify({
                type: 'typing',
                thread_id: this.threadId,
                is_typing: false
            }));
        }, 1000);
    }
    
    setMode(mode) {
        this.currentMode = mode;
        
        // Update button styles
        document.getElementById('conversation-btn').classList.toggle('active', mode === 'conversation');
        document.getElementById('coder-btn').classList.toggle('active', mode === 'coder');
        
        // Add system message
        this.addSystemMessage(`Switched to ${mode} mode`);
    }
    
    showMyThread() {
        document.getElementById('my-thread').classList.remove('hidden');
        document.getElementById('others-threads').classList.add('hidden');
        document.getElementById('my-thread-tab').classList.add('active');
        document.getElementById('others-thread-tab').classList.remove('active');
        this.showOthers = false;
    }
    
    showOthersView() {
        document.getElementById('my-thread').classList.add('hidden');
        document.getElementById('others-threads').classList.remove('hidden');
        document.getElementById('my-thread-tab').classList.remove('active');
        document.getElementById('others-thread-tab').classList.add('active');
        this.showOthers = true;
        this.updateOthersDisplay();
    }
    
    hideOthersView() {
        this.showMyThread();
    }
    
    updateOthersDisplay() {
        const othersList = document.getElementById('others-list');
        othersList.innerHTML = '';
        
        for (const [threadId, thread] of this.otherThreads) {
            const threadDiv = document.createElement('div');
            threadDiv.className = 'other-thread';
            
            const preview = thread.messages.length > 0 
                ? thread.messages[thread.messages.length - 1].content.substring(0, 50) + '...'
                : 'No messages yet';
            
            threadDiv.innerHTML = `
                <div class="other-thread-header">
                    <span class="other-thread-user">${thread.nickname}</span>
                    <span class="other-thread-status">${thread.isGenerating ? 'Generating...' : 'Idle'}</span>
                </div>
                <div class="other-thread-preview">${this.escapeHtml(preview)}</div>
            `;
            
            othersList.appendChild(threadDiv);
        }
    }
    
    updateMyNickname() {
        document.getElementById('my-nickname').textContent = this.nickname;
    }
    
    updateUserCount() {
        // This would need to be implemented with server-side user count
        // For now, we'll estimate based on other threads
        const count = this.otherThreads.size + 1;
        document.getElementById('user-count').textContent = `👥 ${count} user${count !== 1 ? 's' : ''}`;
    }
    
    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        const dotElement = document.querySelector('.status-dot');
        
        statusElement.textContent = status;
        
        switch (status) {
            case 'Connected':
                dotElement.style.background = '#00E5A8';
                break;
            case 'Disconnected':
            case 'Error':
                dotElement.style.background = '#FF4F77';
                break;
            default:
                dotElement.style.background = '#FFC107';
        }
    }
    
    enableInput() {
        document.getElementById('user-input').disabled = false;
        document.getElementById('send-btn').disabled = false;
    }
    
    disableInput() {
        document.getElementById('user-input').disabled = true;
        document.getElementById('send-btn').disabled = true;
    }
    
    copyRoomUrl() {
        const url = window.location.href;
        navigator.clipboard.writeText(url).then(() => {
            const btn = document.getElementById('copy-room');
            const originalText = btn.textContent;
            btn.textContent = '✓';
            setTimeout(() => {
                btn.textContent = originalText;
            }, 2000);
        });
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('my-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    getOrdinal(num) {
        const suffixes = ['th', 'st', 'nd', 'rd'];
        const v = num % 100;
        return suffixes[(v - 20) % 10] || suffixes[v] || suffixes[0];
    }
    
    getNicknameForUser(userId) {
        // This would need to be implemented with server-side user tracking
        return `@user-${userId.substring(0, 8)}`;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new CollaborativeApp();
});
