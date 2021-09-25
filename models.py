from typing import Any, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class User:
    sid: str
    username: str
    room_name: str


@dataclass
class Message:
    user: User
    message: str
    timestamp: str  # ISO


@dataclass
class Room:
    user_ids: List[str]
    messages: List[Message]
