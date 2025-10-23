#!/usr/bin/env python3
"""
Gummy Collaborative - Multi-User AI Chat Platform
FastAPI WebSocket server with fair job queuing and live streaming mirrors
"""

import asyncio
import json
import uuid
import time
import random
import socket
import os
from collections import deque
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set
from datetime import datetime

import aiohttp
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "gemma3:4b"
MAX_WORKERS = int(os.environ.get("WORKERS", "1"))  # Default to 1 worker
MAX_THREAD_HISTORY = 50  # Ring buffer size for thread context

# Friendly animal names for random user IDs
ANIMAL_NAMES = ["llama", "alpaca", "vicuna", "guanaco", "camel", "dromedary"]

@dataclass
class UserInfo:
    user_id: str
    nickname: str
    websocket: WebSocket
    joined_at: float
    thread_id: str

@dataclass
class Job:
    job_id: str
    room_id: str
    thread_id: str
    user_id: str
    messages: List[dict]
    enqueued_at: float

class RoomState:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.users: Dict[str, UserInfo] = {}
        self.threads: Dict[str, List[dict]] = {}  # thread_id -> message history
        self.pending_jobs: deque = deque()
        self.rr_order: deque = deque()  # Round-robin order of user_ids
        self.current_job: Optional[Job] = None
        self.worker_count = 0
        self.created_at = time.time()
        
        # Performance tracking for ETA estimation
        self.generation_times: deque = deque(maxlen=20)  # Rolling window
        self.last_generation_end = None

    def add_user(self, user_info: UserInfo):
        """Add user to room and round-robin queue"""
        self.users[user_info.user_id] = user_info
        
        # Add to round-robin if not already present
        if user_info.user_id not in self.rr_order:
            self.rr_order.append(user_info.user_id)
        
        # Initialize thread if not exists
        if user_info.thread_id not in self.threads:
            self.threads[user_info.thread_id] = []

    def remove_user(self, user_id: str):
        """Remove user from room"""
        if user_id in self.users:
            del self.users[user_id]
        
        # Remove from round-robin
        if user_id in self.rr_order:
            self.rr_order.remove(user_id)
        
        # Cancel any pending jobs for this user
        self.pending_jobs = deque([job for job in self.pending_jobs if job.user_id != user_id])

    def enqueue_job(self, job: Job) -> int:
        """Enqueue job and return position in queue"""
        self.pending_jobs.append(job)
        
        # Add user to round-robin if not present
        if job.user_id not in self.rr_order:
            self.rr_order.append(job.user_id)
        
        # Calculate position for this user
        position = 1
        for pending_job in self.pending_jobs:
            if pending_job.user_id == job.user_id and pending_job.job_id != job.job_id:
                position += 1
        
        return position

    def get_next_job(self) -> Optional[Job]:
        """Get next job using round-robin fairness"""
        if not self.pending_jobs:
            return None
        
        # Find next user in round-robin who has pending jobs
        attempts = 0
        while attempts < len(self.rr_order):
            if not self.rr_order:
                break
                
            user_id = self.rr_order.popleft()
            
            # Find first job for this user
            for i, job in enumerate(self.pending_jobs):
                if job.user_id == user_id:
                    self.pending_jobs.remove(job)
                    self.rr_order.append(user_id)  # Put user back at end
                    return job
            
            # No jobs for this user, put them back at end
            self.rr_order.append(user_id)
            attempts += 1
        
        return None

    def estimate_eta(self, position: int) -> int:
        """Estimate ETA in seconds based on recent generation times"""
        if not self.generation_times:
            return position * 15  # Default 15s per job
        
        avg_time = sum(self.generation_times) / len(self.generation_times)
        return int(position * avg_time)

    def record_generation_time(self, duration: float):
        """Record generation time for ETA estimation"""
        self.generation_times.append(duration)

# Global room state
rooms: Dict[str, RoomState] = {}

# FastAPI app
app = FastAPI(title="Gummy Collaborative", version="1.0.0")

def generate_room_id() -> str:
    """Generate a friendly room ID"""
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))

def generate_user_id() -> str:
    """Generate a friendly user ID"""
    animal = random.choice(ANIMAL_NAMES)
    number = random.randint(1, 999)
    return f"{animal}-{number}"

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

async def stream_ollama(messages: List[dict], model: str = DEFAULT_MODEL):
    """Stream from Ollama API"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": True
                },
                timeout=aiohttp.ClientTimeout(total=120)
            ) as resp:
                if resp.status != 200:
                    yield f"Error: Ollama returned status {resp.status}"
                    return
                
                async for line in resp.content:
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            content = chunk.get("message", {}).get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except asyncio.TimeoutError:
            yield "Error: Request timeout. The model might be too slow."
        except Exception as e:
            yield f"Error: {str(e)}"

async def broadcast_to_room(room_id: str, message: dict, exclude_user: Optional[str] = None):
    """Broadcast message to all users in room"""
    if room_id not in rooms:
        return
    
    room = rooms[room_id]
    disconnected_users = []
    
    for user_id, user_info in room.users.items():
        if exclude_user and user_id == exclude_user:
            continue
        
        try:
            await user_info.websocket.send_text(json.dumps(message))
        except:
            disconnected_users.append(user_id)
    
    # Clean up disconnected users
    for user_id in disconnected_users:
        room.remove_user(user_id)

async def worker_loop(room_id: str, worker_id: int):
    """Worker loop for processing jobs"""
    if room_id not in rooms:
        return
    
    room = rooms[room_id]
    room.worker_count += 1
    
    print(f"Worker {worker_id} started for room {room_id}")
    
    try:
        while room_id in rooms:  # Continue while room exists
            job = room.get_next_job()
            
            if not job:
                await asyncio.sleep(0.1)
                continue
            
            print(f"Worker {worker_id} processing job for user {job.user_id}")
            
            # Check if user still exists
            if job.user_id not in room.users:
                print(f"User {job.user_id} no longer exists, skipping job")
                continue
            
            room.current_job = job
            start_time = time.time()
            
            # Announce generation start
            await broadcast_to_room(room_id, {
                "type": "generation_start",
                "user_id": job.user_id,
                "thread_id": job.thread_id,
                "nickname": room.users[job.user_id].nickname
            })
            
            # Stream from Ollama
            full_response = ""
            try:
                async for chunk in stream_ollama(job.messages, DEFAULT_MODEL):
                    full_response += chunk
                    
                    # Broadcast chunk to all users
                    await broadcast_to_room(room_id, {
                        "type": "chunk",
                        "thread_id": job.thread_id,
                        "user_id": job.user_id,
                        "delta": chunk
                    })
                
                # Add response to thread history
                if job.thread_id in room.threads:
                    room.threads[job.thread_id].append({
                        "role": "assistant",
                        "content": full_response,
                        "timestamp": time.time()
                    })
                    
                    # Trim history to max size
                    if len(room.threads[job.thread_id]) > MAX_THREAD_HISTORY:
                        room.threads[job.thread_id] = room.threads[job.thread_id][-MAX_THREAD_HISTORY:]
                
                # Record generation time
                duration = time.time() - start_time
                room.record_generation_time(duration)
                
            except Exception as e:
                error_msg = f"Generation error: {str(e)}"
                await broadcast_to_room(room_id, {
                    "type": "chunk",
                    "thread_id": job.thread_id,
                    "user_id": job.user_id,
                    "delta": error_msg
                })
            
            # Announce generation done
            await broadcast_to_room(room_id, {
                "type": "generation_done",
                "user_id": job.user_id,
                "thread_id": job.thread_id
            })
            
            room.current_job = None
    
    except Exception as e:
        print(f"Worker {worker_id} error: {e}")
    finally:
        room.worker_count -= 1
        print(f"Worker {worker_id} stopped for room {room_id}")

# Routes
@app.get("/")
async def landing_page():
    """Serve landing page for room creation/joining"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gummy Collaborative</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #0A0B10;
                color: #EAEAF0;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                max-width: 500px;
                text-align: center;
            }
            .logo {
                font-size: 48px;
                font-weight: bold;
                margin-bottom: 20px;
                text-shadow: 0 0 20px rgba(255,79,119,.5);
            }
            .subtitle {
                color: #9AA0B3;
                margin-bottom: 40px;
            }
            .button {
                background: linear-gradient(135deg, #FF4F77, #FF6F91);
                color: white;
                border: none;
                padding: 16px 32px;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                margin: 10px;
                transition: all 0.2s;
                box-shadow: 0 0 25px rgba(255,79,119,.35);
            }
            .button:hover {
                transform: translateY(-2px);
                box-shadow: 0 0 35px rgba(255,79,119,.6);
            }
            .input {
                background: #0e1118;
                border: 1px solid #232334;
                color: #EAEAF0;
                padding: 16px;
                border-radius: 12px;
                font-size: 16px;
                width: 100%;
                margin: 10px 0;
                box-sizing: border-box;
            }
            .input:focus {
                outline: none;
                border-color: rgba(255,255,255,.22);
                box-shadow: 0 0 0 2px rgba(255,255,255,.22);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <img src="/static/gummy-logo.svg" alt="Gummy" style="height: 60px; width: auto;" />
            </div>
            <div class="subtitle">Collaborative AI Chat Platform</div>
            
            <button class="button" onclick="createRoom()">Create Room</button>
            
            <div style="margin: 30px 0;">
                <div style="color: #9AA0B3; margin-bottom: 10px;">Or join an existing room:</div>
                <input type="text" id="roomId" class="input" placeholder="Enter room ID">
                <button class="button" onclick="joinRoom()">Join Room</button>
            </div>
        </div>
        
        <script>
            function createRoom() {
                fetch('/api/create-room', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => {
                        window.location.href = `/room/${data.room_id}`;
                    });
            }
            
            function joinRoom() {
                const roomId = document.getElementById('roomId').value.trim();
                if (roomId) {
                    window.location.href = `/room/${roomId}`;
                }
            }
            
            // Allow Enter key in input
            document.getElementById('roomId').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    joinRoom();
                }
            });
        </script>
    </body>
    </html>
    """)

@app.post("/api/create-room")
async def create_room():
    """Create a new room"""
    room_id = generate_room_id()
    rooms[room_id] = RoomState(room_id)
    
    # Start workers for this room
    for i in range(MAX_WORKERS):
        asyncio.create_task(worker_loop(room_id, i))
    
    return {"room_id": room_id}

@app.get("/room/{room_id}")
async def room_page(room_id: str):
    """Serve collaborative room page"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Read the collaborative.html file and inject the room ID
    try:
        with open('static/collaborative.html', 'r') as f:
            html_content = f.read()
        
        # Replace the placeholder with the actual room ID
        html_content = html_content.replace('window.ROOM_ID = \'loading...\';', f'window.ROOM_ID = \'{room_id}\';')
        
        return HTMLResponse(html_content)
    except FileNotFoundError:
        # Fallback to inline HTML if file not found
        return HTMLResponse("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Gummy Room</title>
            <link rel="stylesheet" href="/static/collaborative.css">
        </head>
        <body>
            <div id="app">
                <!-- Nickname Modal -->
                <div id="nickname-modal" class="modal">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h2>Join Room</h2>
                        </div>
                        <div class="modal-body">
                            <p>What should we call you?</p>
                            <input type="text" id="nickname-input" placeholder="Enter your nickname (optional)" maxlength="20">
                            <div class="modal-actions">
                                <button id="join-btn" class="btn-primary">Join Room</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Main App -->
                <div id="main-app" class="main-app hidden">
                    <!-- Header -->
                    <div class="header">
                        <div class="header-content">
                            <div class="logo">
                                <img src="/static/gummy-logo.svg" alt="Gummy" class="logo-img" />
                            </div>
                            <div class="header-right">
                                <div class="room-info">
                                    <div class="room-id" id="room-pill" title="Tap to copy room URL">
                                        <span>Room: </span>
                                        <code id="room-display">""" + room_id + """</code>
                                        <button id="copy-room" class="copy-btn" title="Copy room URL">📋 Copy</button>
                                    </div>
                                    <div class="user-count">
                                        <span id="user-count">👥 1 user</span>
                                    </div>
                                </div>
                                <div class="connection-badge">
                                    <div class="status-dot"></div>
                                    <span id="connection-status">Connecting...</span>
                                </div>
                                <div class="mode-selector">
                                    <button class="mode-btn active" id="conversation-btn">Conversation</button>
                                    <button class="mode-btn" id="coder-btn">Coder</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Queue Position Pill -->
                    <div id="queue-pill" class="queue-pill hidden">
                        <span id="queue-text">⏳ 2nd in queue (~18s)</span>
                    </div>

                    <!-- Generation Banner -->
                    <div id="generation-banner" class="generation-banner hidden">
                        <span id="generation-text">🤖 Generating for @alice...</span>
                    </div>

                    <!-- Main Content -->
                    <div class="content">
                        <!-- Chat Area -->
                        <div class="chat-container">
                            <div class="thread-tabs">
                                <button class="thread-tab active" id="my-thread-tab">My Chat</button>
                                <button class="thread-tab" id="others-thread-tab">View Others</button>
                            </div>
                            
                            <div class="chat-area">
                                <!-- My Thread -->
                                <div id="my-thread" class="thread active">
                                    <div class="thread-header">
                                        <span class="thread-title">My Chat</span>
                                        <span class="thread-user" id="my-nickname">@user</span>
                                    </div>
                                    <div class="messages" id="my-messages">
                                        <div class="message assistant">
                                            <div class="message-content">
                                                <p>Hello! I'm ready to help. Choose between <strong>Conversation</strong> mode for general chat or <strong>Coder</strong> mode for programming assistance.</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Others Threads Sidebar -->
                                <div id="others-threads" class="others-threads hidden">
                                    <div class="others-header">
                                        <h3>Other Conversations</h3>
                                        <button id="close-others" class="close-btn">✕</button>
                                    </div>
                                    <div class="others-list" id="others-list">
                                        <!-- Other threads will be populated here -->
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Input Area -->
                        <div class="input-container">
                            <div class="input-wrapper">
                                <textarea 
                                    id="user-input" 
                                    class="input-field" 
                                    placeholder="Ask anything…" 
                                    rows="1"
                                    disabled
                                ></textarea>
                                <button class="send-btn" id="send-btn" disabled>
                                    <img src="/static/send-arrow.svg" alt="Send" class="send-arrow" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="/static/collaborative.js"></script>
        <script>
            // Initialize the app with room ID
            window.ROOM_ID = '""" + room_id + """';
        </script>
        </body>
        </html>
        """)

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for room communication"""
    await websocket.accept()
    
    if room_id not in rooms:
        await websocket.close(code=1000, reason="Room not found")
        return
    
    room = rooms[room_id]
    user_id = None
    
    try:
        while True:
            data = await websocket.receive_text()
            print(f"WebSocket received data: {data}")
            
            try:
                message = json.loads(data)
                print(f"WebSocket parsed message: {message}")
            except json.JSONDecodeError as e:
                print(f"WebSocket JSON decode error: {e}")
                continue
            
            if not isinstance(message, dict) or "type" not in message:
                print(f"WebSocket invalid message format: {message}")
                continue
            
            if message["type"] == "join":
                # User joining room
                nickname = message.get("nickname") or ""
                nickname = nickname.strip() if nickname else ""
                if not nickname:
                    nickname = f"@{generate_user_id()}"
                elif not nickname.startswith("@"):
                    nickname = f"@{nickname}"
                
                user_id = str(uuid.uuid4())
                thread_id = str(uuid.uuid4())
                
                user_info = UserInfo(
                    user_id=user_id,
                    nickname=nickname,
                    websocket=websocket,
                    joined_at=time.time(),
                    thread_id=thread_id
                )
                
                room.add_user(user_info)
                
                # Send join confirmation
                await websocket.send_text(json.dumps({
                    "type": "joined",
                    "user_id": user_id,
                    "thread_id": thread_id,
                    "nickname": nickname,
                    "room_id": room_id
                }))
                
                # Broadcast user joined to others
                await broadcast_to_room(room_id, {
                    "type": "user_joined",
                    "user_id": user_id,
                    "nickname": nickname
                }, exclude_user=user_id)
                
            elif message["type"] == "message" and user_id:
                # User sending message
                content = message.get("content") or ""
                content = content.strip() if content else ""
                if not content:
                    continue
                
                thread_id = message.get("thread_id", room.users[user_id].thread_id)
                
                # Add user message to thread history
                if thread_id not in room.threads:
                    room.threads[thread_id] = []
                
                user_message = {
                    "role": "user",
                    "content": content,
                    "timestamp": time.time()
                }
                room.threads[thread_id].append(user_message)
                
                # Prepare messages for Ollama (include recent context)
                messages = room.threads[thread_id][-20:]  # Last 20 messages
                
                # Create job
                job = Job(
                    job_id=str(uuid.uuid4()),
                    room_id=room_id,
                    thread_id=thread_id,
                    user_id=user_id,
                    messages=messages,
                    enqueued_at=time.time()
                )
                
                # Enqueue job
                position = room.enqueue_job(job)
                eta = room.estimate_eta(position)
                print(f"Enqueued job for user {user_id}, position {position}, eta {eta}s")
                
                # Notify user of queue position
                await websocket.send_text(json.dumps({
                    "type": "enqueued",
                    "job_id": job.job_id,
                    "position": position,
                    "eta_seconds": eta
                }))
                
                # Broadcast to room
                await broadcast_to_room(room_id, {
                    "type": "message_added",
                    "user_id": user_id,
                    "thread_id": thread_id,
                    "content": content,
                    "nickname": room.users[user_id].nickname
                })
            
            elif message["type"] == "typing" and user_id:
                # Typing indicator
                is_typing = message.get("is_typing", False)
                thread_id = message.get("thread_id", room.users[user_id].thread_id)
                
                await broadcast_to_room(room_id, {
                    "type": "typing",
                    "user_id": user_id,
                    "thread_id": thread_id,
                    "is_typing": is_typing,
                    "nickname": room.users[user_id].nickname
                }, exclude_user=user_id)
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user {user_id}")
        pass
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if user_id and room_id in rooms:
            room.remove_user(user_id)
            # Broadcast user left
            await broadcast_to_room(room_id, {
                "type": "user_left",
                "user_id": user_id
            })

@app.get("/ngrok-status")
async def ngrok_status():
    """Check if ngrok is active (keep compatibility)"""
    try:
        import requests
        response = requests.get('http://localhost:4040/api/tunnels', timeout=1)
        if response.status_code == 200:
            data = response.json()
            return {"ngrok_active": len(data.get('tunnels', [])) > 0}
    except:
        pass
    return {"ngrok_active": False}

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    print("=" * 60)
    print("Gummy Collaborative - Multi-User AI Chat Platform")
    print("=" * 60)
    
    local_ip = get_local_ip()
    print(f"🌐 Server starting on:")
    print(f"   Local:   http://localhost:5006")
    print(f"   Network: http://{local_ip}:5006")
    print(f"   Workers: {MAX_WORKERS}")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=5006, log_level="info")
