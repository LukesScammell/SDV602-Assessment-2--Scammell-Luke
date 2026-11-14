import threading
from queue import Empty, Queue

import FreeSimpleGUI as sg

import config
from view.chat_view import ChatView


class ChatController:
    def __init__(self, username, message_repository, session_id):
        self.message_repository = message_repository
        self.username = username
        self.session_id = str(session_id)

        self.view = ChatView()

        self.results = Queue()
        self.stop_event = threading.Event()
        self.refresh_requested = threading.Event()
        self.refresh_requested.set()

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

    def process_results(self):
        """Update the GUI using results from the worker thread."""
        while True:
            try:
                result_type, result = self.results.get_nowait()
            except Empty:
                break

            if result_type == "messages":
                self.view.update_messages(result)

            elif result_type == "error":
                print(f"Chat refresh error: {result}")

    def run(self):
        self.worker = threading.Thread(target=self.message_worker, daemon=True)
        self.worker.start()

        try:
            while True:
                event, values = self.view.read(timeout=100)

                self.process_results()

                if event == sg.WIN_CLOSED:
                    break

                if event == "Send":
                    text = values["-CHAT-"]

                    if text.strip():
                        self.message_repository.create_message(self.username, text, self.session_id)
                        self.view.clear_input()
                        self.refresh_requested.set()

        finally:
            self.stop_event.set()
            self.refresh_requested.set()
            self.worker.join(timeout=2)
            self.view.close()