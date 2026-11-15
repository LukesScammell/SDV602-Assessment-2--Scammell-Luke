import FreeSimpleGUI as sg
import matplotlib.pyplot as plt

from view.workspace_view import WorkspaceView
from controller.dataset_controller import DatasetController
from controller.chat_controller import ChatController


class WorkspaceController:
    def __init__(self, username, session_repository, dataset_repository, message_repository):
        self.username = username
        self.session_repository = session_repository
        self.dataset_repository = dataset_repository
        self.message_repository = message_repository

        self.view = WorkspaceView(username)
        self.sessions = []
        self.active_chats = {}
        self.active_datasets = {}

    def refresh_sessions(self):
        self.sessions = self.session_repository.all()
        self.view.update_sessions(self.sessions)
    
    def get_selected_session(self, values):
        if not values["-SESSIONS-"]:
            sg.popup_error("Please select a session.")
            return None

        indexes = self.view.window["-SESSIONS-"].get_indexes()
        
        if not indexes:
            return None

        return self.sessions[indexes[0]]

    def create_session(self, values):
        name = values["-NAME-"].strip()
        description = values["-DESCRIPTION-"].strip()

        if not name:
            sg.popup_error("Please enter a session name.")
            return

        self.session_repository.create_session(name, self.username, description)

        sg.popup("Session created successfully.")
        self.refresh_sessions()

    def delete_session(self, values):
        session = self.get_selected_session(values)

        if session is None:
            return

        if session.owner != self.username:
            sg.popup_error("You can only delete your own sessions.")
            return
        
        session_id = str(session.session_id)

        if (session_id in self.active_chats or session_id in self.active_datasets):
            sg.popup_error("Close this session's dataset browser and chat before deleting it.")
            return

        confirm = sg.popup_yes_no(f"Delete session '{session.name}'?")

        if confirm != "Yes":
            return

        deleted = self.session_repository.delete_session(session_id, self.username)

        if deleted:
            sg.popup("Session deleted.")
            self.refresh_sessions()
        else:
            sg.popup_error("Unable to delete session.")

    
    def open_session(self, values):
        session = self.get_selected_session(values)

        if session is None:
            return

        session_id = str(session.session_id)

        if session_id in self.active_chats:
            sg.popup("This session's chat is already open.")
            return

        if session_id in self.active_datasets:
            sg.popup("This session's dataset browser is already open.")
            return

        dataset = DatasetController(self.username, session, self.dataset_repository)

        self.active_datasets[session_id] = dataset

        try:
            dataset.start()
        except Exception:
            self.active_datasets.pop(session_id, None)
            dataset.close()
            raise
    

    def close_dataset(self, session_id, open_chat=False):
        dataset = self.active_datasets.pop(session_id, None)

        if dataset is None:
            return

        session = dataset.session
        dataset.close()

        if open_chat and session_id not in self.active_chats:
            chat = ChatController(self.username, self.message_repository, session.session_id, session.name)

            self.active_chats[session_id] = chat
            chat.start()

    def close_chat(self, session_id):
        chat = self.active_chats.pop(session_id, None)

        if chat is not None:
            chat.close()

    
    def run(self):
        try:
            self.refresh_sessions()

            while True:
                window, event, values = sg.read_all_windows(
                    timeout=100
                )

                # Process pending Matplotlib GUI events.
                plt.pause(0.001)

                # Process incoming chat messages.
                for chat in list(self.active_chats.values()):
                    chat.process_results()

                if window is None:
                    continue

                # Workspace events.
                if window == self.view.window:
                    if event in (sg.WIN_CLOSED, "Exit"):
                        break

                    if event == "Refresh":
                        self.refresh_sessions()

                    elif event == "Open Session":
                        self.open_session(values)

                    elif event == "Create Session":
                        self.create_session(values)

                    elif event == "Delete Session":
                        self.delete_session(values)

                    continue

                # Dataset browser events.
                dataset_handled = False

                for session_id, dataset in list(self.active_datasets.items()):
                    if window == dataset.view.window:
                        dataset_handled = True

                        if event == sg.WIN_CLOSED:
                            self.close_dataset(session_id)

                        elif event == "Continue to Chat":
                            self.close_dataset(session_id, open_chat=True)

                        else:
                            dataset.handle_event(event, values)

                        break

                if dataset_handled:
                    continue

                # Chat events.
                for session_id, chat in list(self.active_chats.items()):
                    if window == chat.view.window:
                        if event == sg.WIN_CLOSED:
                            self.close_chat(session_id)

                        else:
                            chat.handle_event(event, values)

                        break

        finally:
            for session_id in list(self.active_datasets):
                self.close_dataset(session_id)

            for session_id in list(self.active_chats):
                self.close_chat(session_id)

            self.view.close()
