from datetime import datetime, timezone

from bson import ObjectId

import config
from data.database_manager import DatabaseManager
from model.remote_dataset import RemoteDataset


class DatasetRepository:
    def __init__(self):
        self.db = DatabaseManager.getInstance()

    def upload_dataset(self, name, session_id, uploaded_by, records):
        if not name or not name.strip():
            raise ValueError("Dataset name cannot be empty.")

        if not session_id:
            raise ValueError("Session ID is required.")

        if not uploaded_by or not uploaded_by.strip():
            raise ValueError("Uploader is required.")

        if not records:
            raise ValueError("Dataset cannot be empty.")

        if not all(isinstance(row, dict) for row in records):
            raise ValueError("Dataset records must be dictionaries.")

        columns = set(records[0].keys())

        if not columns or any(
            set(row.keys()) != columns for row in records
        ):
            raise ValueError("Dataset columns must match.")

        document = {
            "name": name.strip(),
            "session_id": str(session_id),
            "uploaded_by": uploaded_by.strip(),
            "records": records,
            "uploaded_at": datetime.now(timezone.utc),
        }

        return self.db.insert_one(config.DATA_SOURCES_COLLECTION, document)

    def all_for_session(self, session_id):
        collection = self.db.get_collection(config.DATA_SOURCES_COLLECTION)

        documents = collection.find({
            "session_id": str(session_id),
        }).sort("uploaded_at", -1)

        return [
            RemoteDataset.from_document(document)
            for document in documents
        ]

    def find_by_id(self, dataset_id, session_id):
        try:
            object_id = ObjectId(str(dataset_id))
        except (TypeError, ValueError):
            return None

        collection = self.db.get_collection(config.DATA_SOURCES_COLLECTION)

        document = collection.find_one({
            "_id": object_id,
            "session_id": str(session_id),
        })

        if document is None:
            return None

        return RemoteDataset.from_document(document)