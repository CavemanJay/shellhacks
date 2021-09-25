from typing import List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class User:
    sid: str
    username: str


@dataclass
class Message:
    timestamp: datetime
    user: User
    message: str


@dataclass
class Room:
    users: List[User]
    messages: List[Message]
