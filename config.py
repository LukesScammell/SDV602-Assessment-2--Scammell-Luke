import os

MONGO_URI = os.environ["SDV602_MONGO_URI"]

if not MONGO_URI:
    raise RuntimeError(
        "MongoDB connection string missing. "
        "Set the SDV602_MONGO_URI environment variable."
    )

DB_NAME = "sdv602_des"
DATA_SOURCES_COLLECTION = "data_sources"
CHAT_MESSAGES_COLLECTION = "chat_messages"
USER_COLLECTION = "users"
SESSIONS_COLLECTION = "des_sessions"

POLL_RATE = 1000