from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Union
from dotenv import load_dotenv
load_dotenv()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        del self.active_connections[client_id]

    async def send_personal_message(self, data: dict, websocket: WebSocket):
        await websocket.send_json(data)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)
            
manager = ConnectionManager()

app = FastAPI()
@app.get("/")
def read_root():
    return "Welcome to the backend server for Beacon's live demo"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.send_personal_message(data, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        
