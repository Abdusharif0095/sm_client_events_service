import asyncio
import threading
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from fastapi.responses import RedirectResponse
from lib.acl import JWTpayload
from src.consumers.v1 import client_events_consumer
import src.endpoints.v1.main as websockets
from src.endpoints.v1.main import manager
from fastapi.middleware.cors import CORSMiddleware
import time

def create_application() -> FastAPI:
    application = FastAPI(
        title="SM platform",
        description="SM Client Events Service.",
        version="1.0.0",
        openapi_url="/client/events/openapi.json",
        docs_url="/client/events/docs")
    application.include_router(websockets.router, prefix='/client/events')
    return application

app = create_application()

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    response.headers["X-Process-App"] = "Time took to process the request and return response is {} sec".format(time.time() - start_time)
    return response

@app.get('/')
def index():
    return RedirectResponse("/client/events/docs")



@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=asyncio.run, args=(client_events_consumer.run(),))
    thread.start()
