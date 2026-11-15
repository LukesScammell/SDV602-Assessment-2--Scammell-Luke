class ChatMessage:
    def __init__(self, username, text, timestamp=None, session_id=None):
        self.username = username
        self.text = text
        self.timestamp = timestamp
        self.session_id = session_id
