from pprint import pprint
from typing import Dict

import socketio
from aiohttp import web
from loguru import logger

from models import Room, User

server = socketio.AsyncServer(async_mode="aiohttp")
app = web.Application()
server.attach(app)

users = {}
rooms = {'general': Room([], [])}


async def move_user_to_room(room_name: str, user: User):
    server.enter_room(user.sid, room_name)
    if room_name not in rooms:
        rooms[room_name] = Room([], [])
    rooms[room_name].users.append(user)
    await server.emit("room_join", room=room_name, data=user.username)


@server.event
async def connect(sid: str, environ: Dict, auth: Dict):
    username = auth.get('username')
    if username:
        user = User(sid, username)
        await move_user_to_room('general', user)
        users[sid] = user
        logger.info("User '{}' has connected", username)
    else:
        # TODO: Error handling for when client doesn't provide username
        server.disconnect(sid)
    # pprint(users)


@server.event
async def list_rooms():
    room_info = [
        {'name': name, 'users': len(room.users)}
        for name, room in rooms.items()
    ]
    return room_info


@server.event
async def disconnect(sid: str):
    user = users[sid]
    del users[sid]
    logger.info("User '{}' disconnected", user.username)
    # TODO: Remove user from any rooms


@server.event
async def chat_message(sid, data):
    user: User = users[sid]
    logger.debug("Message from {}: {}", user.username, data)
    # TODO: Make sure server sends to proper room
    await server.emit('chat_message', skip_sid=sid, data=data)


@server.event
async def switch_room(sid, room_name):
    user: User = users[sid]
    logger.debug("{} is changing rooms to {}", user.username, room_name)
    await move_user_to_room(room_name, user)


@logger.catch
def main():
    web.run_app(app)


if __name__ == "__main__":
    main()
