import socketio
import asyncio


client = socketio.AsyncClient()


@client.event
def chat_message(data):
    print("Received message: ", data)


async def main():
    await client.connect('http://localhost:8080', auth={'username': 'client1'})

    await client.emit('chat_message', "here is the message")
    await client.wait()

if __name__ == "__main__":
    asyncio.run(main())
