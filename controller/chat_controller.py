import threading
from queue import Empty, Queue

import FreeSimpleGUI as sg

import config
from view.chat_view import ChatView

class ChatController:
    def __init__(self, username, message_repository, session_id, session_name="Live Chat"):
        self.message_repository = message_repository
        self.username = username
        self.session_id = str(session_id)

        self.view = ChatView(session_name)

        self.results = Queue()
        self.stop_event = threading.Event()
        self.refresh_requested = threading.Event()

        self.worker = None

    def message_worker(self):
        """Retrieve chat messages without blocking the GUI."""
        while not self.stop_event.is_set():
            try:
                messages = self.message_repository.all(self.session_id)

                self.results.put(("messages", messages))

            except Exception as error:
                self.results.put(("error", str(error)))

            self.refresh_requested.wait(timeout=config.POLL_RATE / 1000)
            self.refresh_requested.clear()
    
    def start(self):
        """Start background polling without blocking the GUI."""
        self.worker = threading.Thread(target=self.message_worker, name=f"Chat-{self.session_id}", daemon=True)
        self.worker.start()

    def process_results(self):
        """Process worker results on the GUI thread."""
        while True:
            try:
                result_type, result = self.results.get_nowait()
            except Empty:
                break

            if result_type == "messages":
                self.view.update_messages(result)

            elif result_type == "error":
                print(f"Chat error: {result}")

    def handle_event(self, event, values):
        """Handle events belonging to this chat window."""
        if event == "Send":
            message = values["-CHAT-"]

            if message.strip():
                try:
                    self.message_repository.create_message(self.username, message, self.session_id)
                    self.view.clear_input()
                    self.refresh_requested.set()

                except Exception as error:
                    self.view.show_error(str(error))

    def close(self):
        """Stop polling and close the chat window."""
        self.stop_event.set()
        self.refresh_requested.set()

        if self.worker is not None:
            self.worker.join(timeout=2)

        self.view.close()

    def run(self):
        """Support standalone chat operation."""
        self.start()

        try:
            while True:
                event, values = self.view.read(timeout=100)

                self.process_results()

                if event == sg.WIN_CLOSED:
                    break

                self.handle_event(event, values)

        finally:
            self.close()