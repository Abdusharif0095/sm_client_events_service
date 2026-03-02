from datetime import datetime
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from lib.websocket_manager import WebsocketConnectionManager
from lib.acl import JWTpayload
from src.models import models
import connections.kafka_connection as kafka
from src.modules.v1 import websocket_response_processer as ws_rp


router = APIRouter(prefix='/v1')
manager = WebsocketConnectionManager()


def add_log(message: str):
    with open("test_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now()} - {message}\n")


@router.post('/send_event')
async def send_sms(user_id: str, request: models.EventModel):
    kafka.send_client_event(user_id, request)
    return "ok"


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        query_params = websocket.query_params
        token = query_params.get("token")

        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        if token.startswith("Bearer "):
            token = token[len("Bearer "):]

        jwt_payload = JWTpayload(token)
        user_id = jwt_payload["user_id"]
        print(f'user_id: {user_id}', flush=True)
        add_log(f"User {user_id} is trying to connect via WebSocket.")
        await manager.connect(websocket, user_id)
        print(f"User {user_id} connected via WebSocket.")
        add_log(f"User {user_id} connected via WebSocket.")

        while True:
            add_log(f"Waiting for message from user {user_id}...")
            data = await websocket.receive_text()
            headers = {
                'x-real-ip': websocket.headers.get('x-real-ip', None)
            }
            await ws_rp.process_received_text(data, headers)
            add_log(f"Received message from user {user_id}: type: {type(data)}, data: {data}")
            print(f"Received message from user {user_id}: {data}", flush=True)

    except WebSocketDisconnect as e:
        manager.disconnect(user_id)
        print(f"User {user_id} disconnected. {e}")
