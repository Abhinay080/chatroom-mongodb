from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from database import add_message, retrieve_messages, create_or_get_conversation, convert_objectid_to_str

app = FastAPI()

# Enable CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[websocket] = username

    def disconnect(self, websocket: WebSocket, conversation_id: str, username: str):
        if websocket in self.active_connections:
            del self.active_connections[websocket]
            # Log the disconnection event (optional)

    async def broadcast(self, message: str, conversation_id: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat/{ehempid1}/{ehempid2}/{username}")
async def websocket_endpoint(websocket: WebSocket, ehempid1: str, ehempid2: str, username: str):
    conversation_id = create_or_get_conversation(ehempid1, ehempid2)
    
    await manager.connect(websocket, username)
    try:
        while True:
            data = await websocket.receive_text()
            # Save message to MongoDB
            add_message(conversation_id, username, data)
            await manager.broadcast(f"{username} says: {data}", conversation_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id, username)
        # await manager.broadcast(f"{username} has left the chat", conversation_id)

@app.get("/messages/{conversation_id}")
async def get_messages(conversation_id: str):
    messages = retrieve_messages(conversation_id)
    messages = convert_objectid_to_str(messages)
    return messages

@app.post("/conversations")
async def create_new_conversation(ehempid1: str, ehempid2: str):
    conversation_id = create_or_get_conversation(ehempid1, ehempid2)
    return {"conversation_id": str(conversation_id)}

@app.get("/conversations")
async def get_existing_conversation(ehempid1: str, ehempid2: str):
    conversation_id = create_or_get_conversation(ehempid1, ehempid2)
    return {"conversation_id": conversation_id}