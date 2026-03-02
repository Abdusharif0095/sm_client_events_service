from fastapi import WebSocket
import json

class WebsocketConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_message_async(self, user_id: str, message: dict):
        json_message = json.dumps(message)
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                print('<<<<<----- Sending message ----->>>>', flush=True)
                await websocket.send_text(json_message)
            except Exception as ex:
                print(f"Error sending message to {user_id}: {ex}")
            return None
        else:
            print(f"User {user_id} not connected")
            return "user_not_connected"


    async def broadcast_async(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)