import asyncio
import tempfile
from pathlib import Path

import socketio

client = socketio.AsyncClient()
CREDS_FILE = Path(
    tempfile.gettempdir(), "shellhacks_chatserver_auth")


@client.event
async def chat_message(data):
    print("Received message: ", data)


@client.event
async def room_join(username: str):
    print(F"SERVER: User {username} has joined the room")


async def main():
    if CREDS_FILE.exists() and CREDS_FILE.read_text():
        username = CREDS_FILE.read_text()
    else:
        username = input("Please enter your username: ")
        CREDS_FILE.write_text(username)
    await client.connect('http://localhost:8080', auth={'username': username})

    await client.emit('chat_message', "here is the message")
    await client.wait()

if __name__ == "__main__":
    asyncio.run(main())
