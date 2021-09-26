from dataclasses import asdict
from datetime import datetime
from pprint import pprint
from typing import Dict

import pymongo
import socketio
from aiohttp import web
from loguru import logger

from models import Message, Room, User
from db import create_room, load_rooms, save_message


server = socketio.AsyncServer(
    async_mode="aiohttp", logger=False, ping_timeout=10000000)  # High ping time out to avoid disconnecting inactive users.
app = web.Application()
server.attach(app)


users: Dict[str, User] = {}
# rooms = {'general': Room([], [])}
rooms = load_rooms()


async def move_user_to_room(room_name: str, user: User):
    server.enter_room(user.sid, room_name)
    if room_name not in rooms:
        rooms[room_name] = Room([], [])
        create_room(room_name)
    rooms[room_name].user_ids.append(user.sid)

    if user.room_name:
        logger.debug("Removing user from old room")
        rooms[user.room_name].user_ids.remove(user.sid)

    user.room_name = room_name
    await server.emit("room_join", room=room_name, data=user.username)


@server.event
async def connect(sid: str, environ: Dict, auth: Dict):
    username = auth.get('username')
    if username:
        user = User(sid, username, None)
        await move_user_to_room('general', user)
        users[sid] = user
        logger.info("User '{}' has connected", username)
    else:
        # TODO: Error handling for when client doesn't provide username
        server.disconnect(sid)


@server.event
async def current_room(sid):
    user: User = users[sid]
    room = user.room_name
    return room


@server.event
async def list_rooms(sid):
    room_info = [
        {'name': name, 'users': len(room.user_ids)}
        for name, room in rooms.items()
    ]
    return room_info


@server.event
async def room_history(sid):
    user: User = users[sid]
    room: Room = rooms[user.room_name]
    return list(map(asdict, room.messages))


@server.event
async def find_user(sid, username: str):
    target_user = [
        user
        for _, user in users.items()
        if user.username == username
    ]

    if not target_user:
        return ''

    user: User = target_user[0]
    return user.room_name


@server.event
async def disconnect(sid: str):
    user: User = users[sid]
    del users[sid]
    logger.info("User '{}' disconnected", user.username)
    rooms[user.room_name].user_ids.remove(sid)


@server.event
async def chat_message(sid, message_text: str):
    user: User = users[sid]
    message = Message(user, message_text, datetime.now().isoformat())
    room: Room = rooms[user.room_name]
    room.messages.append(message)
    save_message(message, user.room_name)
    logger.debug("Message from {} in room {}: {}",
                 user.username, user.room_name, message_text)
    await server.emit('chat_message', room=user.room_name, skip_sid=sid, data=asdict(message))


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
