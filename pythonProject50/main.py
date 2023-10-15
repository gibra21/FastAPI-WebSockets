from fastapi import FastAPI
from multiprocessing import managers
from locale import currency
from sqlite3 import connect
from typing import List
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers = ["*"],


)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def connect(self, websocket:WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket:WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(selfself,message:str,websocket:WebSocket):
        await websocket.send_text(message)

    async def broadcast(self,message:str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# define endpoint
@app.get("/")
def Home():
   return "Welcome home"

@app.websocket("/ws{client_id}")
async def websocket_endpoint(websocket:WebSocket, client_id:int):
    now = datetime.now()
    currency_time = now.strftime("%M:%M")

    try:
        while True:
            date = await(websocket.receive_text())
            message = {"time": currency_time, "client_id": client_id, "message":message}
            await manager.broadcast(json.dumps(message))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        message = {"time": currency_time, "client_id": client_id, "message":message}
        await manager.broadcast(json.dumps(message))
