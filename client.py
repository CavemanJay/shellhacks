import socketio

client = socketio.Client()
client.connect('http://localhost:8080',auth={'username':'client1'})
client.emit('chat_message', "here is the message")
client.disconnect()
