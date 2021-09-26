import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
import socketio
from aioconsole import ainput

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
        _input = await ainput()
        if _input.strip() == '':
            continue
        if _input.lower().strip() in ['/exit', '/quit', '/q']:
            return

        if _input.lower().startswith('/join '):
            room = _input.split(' ')[1]
            await client.emit('switch_room', room)
            await client.sleep(0.5)
            continue

        if _input.lower().strip() == "/rooms":
            await client.emit('list_rooms', callback=display_rooms)
            await client.sleep(0.5)
            continue

        if _input.lower().strip() == "/history":
            await client.emit('room_history', callback=display_room_history)
            await client.sleep(0.5)
            continue

        await client.emit('chat_message', _input)
        await client.sleep(0.5)


async def main():
    if CREDS_FILE.exists() and CREDS_FILE.read_text():
        username = CREDS_FILE.read_text()
    else:
        username = input("Please enter your username: ")
        CREDS_FILE.write_text(username)
    await client.connect('http://localhost:8080', auth={'username': username})

    await read_user_input()
    await client.disconnect()
# TODO: Add /history command
# TODO: Little unrealistic but rough gui if we have time :D
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        exit(1)
