from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Union
from dotenv import load_dotenv

load_dotenv()

from segment_demo import segment_point, segment_text
from audio_utils import generate_stream_input, base64_to_text
from tools_agent import process_agent


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

    async def send_personal_bytes(self, data: bytes, websocket: WebSocket):
        await websocket.send_bytes(data)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = ConnectionManager()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to more restrictive origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return "Welcome to the backend server for Beacon's live demo"


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: Union[str, None] = None):
    if client_id is None:
        client_id = websocket.query_params.get("client_id")

    if client_id is None:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_json()
            event = data["event"]
            try:
                match event:
                    case "segment_point":
                        mask, score = segment_point(data["image"], data["point"])
                        await manager.send_personal_message(
                            {"mask": mask, "score": str(score)}, websocket
                        )
                    case "segment_text":
                        mask, box = segment_text(data["image"], data["text"])
                        await manager.send_personal_message(
                            {"mask": mask, "box": box}, websocket
                        )
                    case "audio_chat":
                        transcript = await base64_to_text(data["audio"])
                        await manager.send_personal_message(
                            {"transcript": transcript}, websocket
                        )
                        audio_stream = await process_agent(transcript)
                        async for chunk in audio_stream:
                            await manager.send_personal_bytes(chunk, websocket)

            except Exception as e:
                print(f"Error: {e}")
                await manager.send_personal_message({"error": str(e)}, websocket)
    except WebSocketDisconnect:
        print("Disconnecting...")
        manager.disconnect(client_id)
