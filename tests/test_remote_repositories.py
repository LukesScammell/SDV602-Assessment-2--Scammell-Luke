import unittest
from unittest.mock import MagicMock, patch
from bson.errors import InvalidId

from bson import ObjectId

from data.session_repository import SessionRepository
from data.message_repository import MessageRepository
from data.dataset_repository import DatasetRepository


class TestSessionRepository(unittest.TestCase):
    def setUp(self):
        self.database = MagicMock()

        with patch(
            "data.session_repository.DatabaseManager.getInstance",
            return_value=self.database,
        ):
            self.repository = SessionRepository()

    def test_create_session(self):
        """Creating a session should save its details."""
        self.repository.create_session(
            "Test Session", "Luke", "Test description"
        )

        collection_name, document = self.database.insert_one.call_args.args

        self.assertEqual(collection_name, "des_sessions")
        self.assertEqual(document["name"], "Test Session")
        self.assertEqual(document["owner"], "Luke")
        self.assertEqual(document["description"], "Test description")

    def test_empty_session_name(self):
        """A session must have a name."""
        with self.assertRaises(ValueError):
            self.repository.create_session("", "Luke")

    def test_empty_session_owner(self):
        """A session must have an owner."""
        with self.assertRaises(ValueError):
            self.repository.create_session("Test Session", "")

    def test_delete_session_owner(self):
        """Deletion must include the session owner."""
        session_id = str(ObjectId())

        collection = self.database.get_collection.return_value
        collection.delete_one.return_value.deleted_count = 1

        result = self.repository.delete_session(session_id, "Luke")

        self.assertTrue(result)

        collection.delete_one.assert_called_once_with(
            {"_id": ObjectId(session_id), "owner": "Luke"}
        )

    def test_delete_session_not_owner(self):
        """Deletion should fail when no owned session matches."""
        session_id = str(ObjectId())

        collection = self.database.get_collection.return_value
        collection.delete_one.return_value.deleted_count = 0

        result = self.repository.delete_session(session_id, "Bob")

        self.assertFalse(result)

    def test_invalid_session_id(self):
        """Invalid session IDs should be rejected."""
        result = self.repository.find_by_id("invalid-id")

        self.assertIsNone(result)


class TestMessageRepository(unittest.TestCase):
    def setUp(self):
        self.database = MagicMock()

        with patch(
            "data.message_repository.DatabaseManager.getInstance",
            return_value=self.database,
        ):
            self.repository = MessageRepository()

    def test_create_message(self):
        """Messages should be saved against their DES session."""
        self.repository.create_message("Luke", "Hello Bob", "session-a")

        collection_name, document = self.database.insert_one.call_args.args

        self.assertEqual(collection_name, "chat_messages")
        self.assertEqual(document["username"], "Luke")
        self.assertEqual(document["text"], "Hello Bob")
        self.assertEqual(document["session_id"], "session-a")

    def test_empty_message(self):
        """Empty chat messages should be rejected."""
        with self.assertRaises(ValueError):
            self.repository.create_message("Luke", "   ", "session-a")

    def test_message_requires_session(self):
        """A message must belong to a DES session."""
        with self.assertRaises(ValueError):
            self.repository.create_message("Luke", "Hello", "")

    def test_messages_filtered_by_session(self):
        """Chat history should be filtered by session ID."""
        collection = self.database.get_collection.return_value
        collection.find.return_value.sort.return_value = []

        result = self.repository.all("session-a")

        collection.find.assert_called_once_with({"session_id": "session-a"})

        self.assertEqual(result, [])


class TestDatasetRepository(unittest.TestCase):
    def setUp(self):
        self.database = MagicMock()

        with patch(
            "data.dataset_repository.DatabaseManager.getInstance",
            return_value=self.database,
        ):
            self.repository = DatasetRepository()

    def test_upload_dataset(self):
        """Valid datasets should be saved."""
        records = [
            {"Period": "2025", "Count": "100"},
            {"Period": "2026", "Count": "120"},
        ]

        self.repository.upload_dataset(
            "Population", "session-a", "Luke", records
        )

        collection_name, document = self.database.insert_one.call_args.args

        self.assertEqual(collection_name, "data_sources")
        self.assertEqual(document["name"], "Population")
        self.assertEqual(document["session_id"], "session-a")
        self.assertEqual(document["uploaded_by"], "Luke")
        self.assertEqual(document["records"], records)

    def test_empty_dataset(self):
        """Empty datasets should be rejected."""
        with self.assertRaises(ValueError):
            self.repository.upload_dataset("Empty", "session-a", "Luke", [])

    def test_mismatched_dataset_columns(self):
        """Every dataset record must have matching columns."""
        records = [
            {"Period": "2025", "Count": "100"},
            {"Year": "2026", "Population": "120"},
        ]

        with self.assertRaises(ValueError):
            self.repository.upload_dataset(
                "Invalid", "session-a", "Luke", records
            )

    def test_datasets_filtered_by_session(self):
        """Only datasets belonging to a session are requested."""
        collection = self.database.get_collection.return_value
        collection.find.return_value.sort.return_value = []

        result = self.repository.all_for_session("session-a")

        collection.find.assert_called_once_with({"session_id": "session-a"})

        self.assertEqual(result, [])

    def test_invalid_dataset_id(self):
        """Invalid dataset IDs should return None."""
        result = self.repository.find_by_id("invalid-id", "session-a")

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
