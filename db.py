
from dataclasses import asdict
from typing import List
from models import Message, Room, User
import pymongo


client = pymongo.MongoClient("mongodb://34.138.239.197/shellhacks")
db = client.get_default_database()
message_collection = db.get_collection("messages")
room_collection = db.get_collection("rooms")


def load_rooms():
    messages = list(message_collection.find())
    rooms = list(room_collection.find())

    x = {
        room['name']: Room([], [
            Message(User(message['user']['sid'],
                         message['user']['username'], room),
                    message['message'],
                    message['timestamp'])
            for message in messages
            if str(message['_id']) in room['messages']
        ])
        for room in rooms
    }
    return x


def create_room(name):
    room_collection.insert_one({'name': name, 'messages': []})


def save_message(message: Message, room_name: str):
    db_message = asdict(message)
    _id = str(message_collection.insert_one(db_message).inserted_id)

    db_room = room_collection.find_one({'name': room_name})
    db_room['messages'].append(_id)
    room_collection.find_one_and_delete({'name': room_name})
    result = room_collection.insert_one(
        {'name': room_name, 'messages': db_room['messages']})
