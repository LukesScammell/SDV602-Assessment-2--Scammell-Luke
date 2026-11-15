import FreeSimpleGUI as sg


class SessionView:
    def __init__(self):
        sg.theme("DarkBlue3")

        layout = [
            [sg.Text("DES Session Browser", font=("Arial", 20))],
            [sg.Text("Select an existing session or create a new one.")],
            [
                sg.Listbox(
                    values=[],
                    size=(60, 10),
                    key="-SESSIONS-",
                    enable_events=True,
                )
            ],
            [
                sg.Text("Session name:", size=(15, 1)),
                sg.Input(key="-NAME-", size=(35, 1)),
            ],
            [
                sg.Text("Description:", size=(15, 1)),
                sg.Input(key="-DESCRIPTION-", size=(35, 1)),
            ],
            [
                sg.Button("Create"),
                sg.Button("Join"),
                sg.Button("Delete"),
                sg.Button("Refresh"),
                sg.Button("Exit"),
            ],
        ]

        self.window = sg.Window("SDV602 - DES Sessions", layout, finalize=True)

    def read(self):
        return self.window.read()

    def update_sessions(self, sessions):
        self.window["-SESSIONS-"].update(
            values=[
                f"{session.name} | Owner: {session.owner}"
                for session in sessions
            ]
        )

    def close(self):
        self.window.close()
