from datetime import datetime

import config

from data.database_manager import DatabaseManager
from model.chat_message import ChatMessage


class MessageRepository:
    def __init__(self):
        self.db = DatabaseManager.getInstance()

    def create_message(self, username, text, session_id, timestamp=None):
        if not session_id:
            raise ValueError("A session ID is required.")

        if not text.strip():
            raise ValueError("Message cannot be empty.")

        if timestamp is None:
            timestamp = datetime.now()

        document = {
            "username": username,
            "text": text.strip(),
            "timestamp": timestamp,
            "session_id": str(session_id),
        }

        return self.db.insert_one(config.CHAT_MESSAGES_COLLECTION, document)

    def all(self, session_id):
        if not session_id:
            raise ValueError("A session ID is required.")

        collection = self.db.get_collection(config.CHAT_MESSAGES_COLLECTION)

        documents = collection.find(
            {
                "session_id": str(session_id),
            }
        ).sort("timestamp", 1)

        messages = []

        for document in documents:
            message = ChatMessage(
                document["username"],
                document["text"],
                document["timestamp"],
                session_id=document["session_id"],
            )
            messages.append(message)

        return messages
