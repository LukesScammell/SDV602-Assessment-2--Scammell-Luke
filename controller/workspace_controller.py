import FreeSimpleGUI as sg

from view.workspace_view import WorkspaceView
from controller.des_controller import DesController

class WorkspaceController:
    def __init__(self, username, session_repository, dataset_repository, message_repository, initial_session_id=None):
        self.username = username
        self.session_repository = session_repository
        self.dataset_repository = dataset_repository
        self.message_repository = message_repository

        self.view = WorkspaceView(username)
        self.sessions = []
        self.active_des = {}
        self.initial_session_id = initial_session_id

    def refresh_sessions(self):
        self.sessions = self.session_repository.all()
        self.view.update_sessions(self.sessions)
    
    def get_selected_session(self, values):
        """Return the session selected in the workspace."""
        if not values["-SESSIONS-"]:
            sg.popup_error("Please select a session.")
            return None

        indexes = self.view.window["-SESSIONS-"].get_indexes()

        if not indexes:
            return None

        return self.sessions[indexes[0]]
    
    def open_initial_session(self):
        """Open a requested DES session after successful login."""
        if self.initial_session_id is None:
            return

        session = self.session_repository.find_by_id(self.initial_session_id)

        if session is None:
            sg.popup_error(
                "The requested DES session does not exist "
                "or the session ID is invalid."
            )
            return

        self.open_des_session(session)
        
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

        if session_id in self.active_des:
            sg.popup_error("Close the DES window before deleting this session.")
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
        """Open the DES session selected in the workspace."""
        session = self.get_selected_session(values)

        if session is None:
            return

        self.open_des_session(session)


    def open_des_session(self, session):
        """Open a DES window for the supplied session."""
        session_id = str(session.session_id)

        if session_id in self.active_des:
            sg.popup("This DES session is already open.")
            return

        des = DesController(self.username, session, self.message_repository, self.dataset_repository)

        self.active_des[session_id] = des

        try:
            des.start()

        except Exception:
            self.active_des.pop(session_id, None)
            des.close()
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

    def close_des(self, session_id):
        """Close one DES window and stop its background worker."""
        des = self.active_des.pop(session_id, None)

        if des is not None:
            des.close()
    
    def run(self):
        """Manage the session browser and all active DES windows."""
        try:
            self.refresh_sessions()
            self.open_initial_session()

            while True:
                window, event, values = sg.read_all_windows(timeout=100)

                for des in list(self.active_des.values()):
                    des.process_results()

                if window is None:
                    continue

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

                for session_id, des in list(self.active_des.items()):
                    if window == des.view.window:
                        if event in (sg.WIN_CLOSED, "Close DES"):
                            self.close_des(session_id)
                        else:
                            des.handle_event(event, values)

                        break

                    if (des.dataset_manager is not None and window == des.dataset_manager.view.window):
                        des.handle_dataset_event(event, values)
                        break

        finally:
            for session_id in list(self.active_des):
                self.close_des(session_id)

            self.view.close()