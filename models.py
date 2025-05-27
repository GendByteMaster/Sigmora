from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict

class User(BaseModel):
    email: str
    password: str
    subscribed: bool = False
    preferences: Dict[str, List[str]] = {"topic": [], "release_time": [], "priority": [], "category": []}

class Notification(BaseModel):
    topic: str
    release_time: datetime
    priority: str
    category: str
    sent_to: List[str] = []

class Token(BaseModel):
    access_token: str
    token_type: str