from typing import Dict
import socketio
from aiohttp import web
from pprint import pprint

socket = socketio.AsyncServer(async_mode="aiohttp")
app = web.Application()
socket.attach(app)

users = {}


@socket.event
def connect(sid: str, environ: Dict, auth: Dict):
    _key = 'username'
    if auth.get(_key):
        users[sid] = auth[_key]
    else:
        # TODO: Error handling for when client doesn't provide username
        socket.disconnect(sid)
    pprint(users)


@socket.event
def disconnect(sid: str):
    del users[sid]


@socket.event
async def chat_message(sid, data):
    print("message ", sid, data)


if __name__ == "__main__":
    web.run_app(app)
