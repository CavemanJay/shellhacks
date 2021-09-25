import socketio
import asyncio


client = socketio.AsyncClient()


@client.event
async def chat_message(data):
    print("Received message: ", data)


@client.event
async def room_join(username: str):
    print(F"SERVER: User {username} has joined the room")


async def main():
    await client.connect('http://localhost:8080', auth={'username': 'client1'})

    await client.emit('chat_message', "here is the message")
    await client.wait()

if __name__ == "__main__":
    asyncio.run(main())
