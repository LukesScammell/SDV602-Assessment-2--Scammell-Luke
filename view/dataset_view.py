import FreeSimpleGUI as sg


class DatasetView:
    def __init__(self, session_name):
        sg.theme("DarkBlue3")

        layout = [
            [sg.Text("Remote Dataset Browser", font=("Arial", 20))],
            [sg.Text(f"Session: {session_name}")],
            [sg.Text("Available datasets:")],
            [sg.Listbox(values=[], size=(65, 10), key="-DATASETS-")],
            [
                sg.Button("Upload CSV"),
                sg.Button("Load Dataset"),
                sg.Button("Refresh"),
                sg.Button("Close"),
            ],
        ]

        self.window = sg.Window(
            f"SDV602 - Remote Datasets - {session_name}", layout, finalize=True
        )

    def update_datasets(self, datasets):
        self.window["-DATASETS-"].update(
            values=[
                f"{dataset.name} | {len(dataset.records)} records"
                f" | ID: {dataset.dataset_id}"
                for dataset in datasets
            ]
        )

    def read(self, timeout=None):
        return self.window.read(timeout=timeout)

    def close(self):
        self.window.close()
