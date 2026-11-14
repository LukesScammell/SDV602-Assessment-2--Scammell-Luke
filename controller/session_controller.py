import FreeSimpleGUI as sg

from view.session_view import SessionView


class SessionController:
    def __init__(self, username, session_repository):
        self.username = username
        self.session_repository = session_repository
        self.view = SessionView()
        self.sessions = []

    def refresh_sessions(self):
        self.sessions = self.session_repository.all()
        self.view.update_sessions(self.sessions)

    def get_selected_session(self, values):
        selected = values["-SESSIONS-"]

        if not selected:
            sg.popup_error("Please select a session.")
            return None

        selected_index = self.view.window["-SESSIONS-"].get_indexes()[0]

        return self.sessions[selected_index]

    def run(self):
        self.refresh_sessions()

        while True:
            event, values = self.view.read()

            if event in (sg.WIN_CLOSED, "Exit"):
                break

            if event == "Refresh":
                self.refresh_sessions()

            elif event == "Create":
                name = values["-NAME-"].strip()
                description = values["-DESCRIPTION-"].strip()

                if not name:
                    sg.popup_error("Please enter a session name.")
                    continue

                self.session_repository.create_session(
                    name,
                    self.username,
                    description,
                )

                sg.popup("Session created successfully.")
                self.refresh_sessions()

            elif event == "Join":
                session = self.get_selected_session(values)

                if session:
                    self.view.close()
                    return session

            elif event == "Delete":
                session = self.get_selected_session(values)

                if session:
                    if session.owner != self.username:
                        sg.popup_error("You can only delete your own sessions.")
                        continue

                    confirm = sg.popup_yes_no(f"Delete session '{session.name}'?")

                    if confirm == "Yes":
                        deleted = self.session_repository.delete_session(
                            str(session.session_id),
                            self.username,
                        )

                        if deleted:
                            sg.popup("Session deleted.")
                            self.refresh_sessions()

        self.view.close()
        return None