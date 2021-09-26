import asyncio
import tempfile
from datetime import datetime
from pathlib import Path

import socketio
from aioconsole import ainput
DELAY = 0.01
client = socketio.AsyncClient()
CREDS_FILE = Path(
    tempfile.gettempdir(), "shellhacks_chatserver_auth")


def display_room_history(message_history):
    for message in message_history:
        timestamp = datetime.fromisoformat(message['timestamp']).time()
        print(timestamp, message['user']['username'] + ":", message['message'])


def display_rooms(rooms):
    for room in rooms:
        print(F"{room['name']} ({room['users']})")


@client.event
async def chat_message(data):
    timestamp = datetime.fromisoformat(data['timestamp']).time()
    print(timestamp, data['user']['username'] + ":", data['message'])


@client.event
async def room_join(username: str):
    print(F"SERVER: User {username} has joined the room")


async def read_user_input():
    while True:
        # print("[+] ", end='')
        _input: str = await ainput()
        if _input.strip() == '':
            continue
        if _input.lower().startswith('/help'):
            print("""Commands available:
            /help: Displays this screen
            /rooms: Displays all available rooms
            /pwr: Displays current room
            /join: Creates a room if it does not exist and joins it, other wise it just joins it
            /history: Displays History of the chat room
            /find: Find a user by username 
            /quit: exit the application""")
            continue
        if _input.lower().strip() in ['/exit', '/quit', '/q']:
            return

        if _input.lower().startswith('/pwr'):
            await client.emit('current_room', callback=print)
            await client.sleep(DELAY)
            continue

        if _input.lower().startswith('/join '):
            room = _input.split(' ')[1]
            await client.emit('switch_room', room)
            await client.sleep(DELAY)
            continue

        if _input.lower().strip() == "/rooms":
            await client.emit('list_rooms', callback=display_rooms)
            await client.sleep(DELAY)
            continue

        if _input.lower().strip() == "/history":
            await client.emit('room_history', callback=display_room_history)
            await client.sleep(DELAY)
            continue

        if _input.lower().strip().startswith("/find"):
            def callback(data):
                print(data)
            [_, user, *_] = _input.strip().split(' ')

            await client.emit('find_user', data=user, callback=callback)
            await client.sleep(DELAY)
            continue

        await client.emit('chat_message', _input)
        await client.sleep(DELAY)


async def main():
    if CREDS_FILE.exists() and CREDS_FILE.read_text():
        username = CREDS_FILE.read_text()
    else:
        username = input("Please enter your username: ")
        CREDS_FILE.write_text(username)
    # await client.connect('http://34.138.239.197:8080', auth={'username': username})
    await client.connect('http://localhost:8080', auth={'username': username})

    await read_user_input()
    await client.disconnect()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        exit(1)