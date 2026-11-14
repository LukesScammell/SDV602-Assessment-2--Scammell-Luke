from datetime import datetime, timezone

import config

from data.database_manager import DatabaseManager
from model.des_session import DesSession


class SessionRepository:
    def __init__(self):
        self.db = DatabaseManager.getInstance()

    def create_session(self, name, owner, description=""):
        name = name.strip()
        owner = owner.strip()

        if not name:
            raise ValueError("Session name cannot be empty.")

        if not owner:
            raise ValueError("Session owner cannot be empty.")

        document = {
            "name": name,
            "owner": owner,
            "description": description.strip(),
            "created_at": datetime.now(timezone.utc),
        }

        return self.db.insert_one(
            config.SESSIONS_COLLECTION,
            document,
        )

    def all(self):
        collection = self.db.get_collection(
            config.SESSIONS_COLLECTION
        )

        documents = collection.find().sort("created_at", -1)

        return [
            DesSession.from_document(document)
            for document in documents
        ]

    def find_by_id(self, session_id):
        from bson import ObjectId

        try:
            object_id = ObjectId(session_id)
        except (TypeError, ValueError):
            return None

        collection = self.db.get_collection(
            config.SESSIONS_COLLECTION
        )

        document = collection.find_one({"_id": object_id})

        if document is None:
            return None

        return DesSession.from_document(document)

    def delete_session(self, session_id, username):
        from bson import ObjectId

        try:
            object_id = ObjectId(session_id)
        except (TypeError, ValueError):
            return False

        collection = self.db.get_collection(
            config.SESSIONS_COLLECTION
        )

        result = collection.delete_one({
            "_id": object_id,
            "owner": username,
        })

        return result.deleted_count == 1