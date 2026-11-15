import FreeSimpleGUI as sg


class WorkspaceView:
    def __init__(self, username):
        sg.theme("DarkBlue3")

        layout = [
            [sg.Text("DES Workspace", font=("Arial", 20))],
            [sg.Text(f"Logged in as: {username}")],
            [sg.Text("Available DES sessions:")],
            [sg.Listbox(values=[], size=(65, 12), key="-SESSIONS-")],
            [
                sg.Text("Session name:", size=(15, 1)),
                sg.Input(key="-NAME-", size=(35, 1)),
            ],
            [
                sg.Text("Description:", size=(15, 1)),
                sg.Input(key="-DESCRIPTION-", size=(35, 1)),
            ],
            [
                sg.Button("Open Session"),
                sg.Button("Create Session"),
                sg.Button("Delete Session"),
                sg.Button("Refresh"),
                sg.Button("Exit"),
            ],
        ]

        self.window = sg.Window(
            "SDV602 - Multi-Session Workspace", layout, finalize=True
        )

    def update_sessions(self, sessions):
        self.window["-SESSIONS-"].update(
            values=[
                f"{session.name} | Owner: {session.owner}"
                for session in sessions
            ]
        )

    def read(self):
        return self.window.read()

    def close(self):
        self.window.close()
