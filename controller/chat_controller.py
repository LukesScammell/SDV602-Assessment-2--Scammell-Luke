from view.chat_view import ChatView
import config
import FreeSimpleGUI as sg


class ChatController:
    def __init__(self, username, message_repository, session_id):
        self.message_repository = message_repository
        self.username = username
        self.session_id = str(session_id)

        self.view = ChatView()
    
    def refresh_messages(self):
        messages = self.message_repository.all(self.session_id)
        self.view.update_messages(messages)

    def run(self):
        self.refresh_messages()
    

        while True:
            event, values = self.view.read(timeout=config.POLL_RATE)

            if event == sg.WIN_CLOSED:
                break

            if event == "__TIMEOUT__":
               self.refresh_messages()

            if event == "Send":
                text = values["-CHAT-"]

                if text.strip():
                    self.message_repository.create_message(self.username, text, self.session_id)
                    self.view.clear_input()
                    self.refresh_messages()

        self.view.close()