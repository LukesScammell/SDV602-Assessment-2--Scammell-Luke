from pathlib import Path

import FreeSimpleGUI as sg
from bson import BSON

from data_visualiser import DataVisualiser
from view.dataset_view import DatasetView


MAX_CSV_BYTES = 10 * 1024 * 1024
MAX_DOCUMENT_BYTES = 15 * 1024 * 1024


class DatasetController:
    def __init__(self, username, session, dataset_repository):
        self.username = username
        self.session = session
        self.repository = dataset_repository
        self.visualiser = DataVisualiser()
        self.view = DatasetView(session.name)
        self.datasets = []

    def refresh_datasets(self):
        self.datasets = self.repository.all_for_session(self.session.session_id)
        self.view.update_datasets(self.datasets)

    def upload_csv(self):
        file_path = sg.popup_get_file("Select a CSV dataset", file_types=[("CSV Files", "*.csv")])

        if not file_path:
            return

        try:
            path = Path(file_path)

            if path.stat().st_size > MAX_CSV_BYTES:
                sg.popup_error("CSV file exceeds the 10 MiB limit.")
                return

            visualiser = DataVisualiser()

            if not visualiser.load_csv(str(path)):
                sg.popup_error("Unable to load the CSV file.")
                return

            records = visualiser.get_data()

            document = {
                "name": path.stem,
                "session_id": str(self.session.session_id),
                "uploaded_by": self.username,
                "records": records,
            }

            if len(BSON.encode(document)) > MAX_DOCUMENT_BYTES:
                sg.popup_error("Dataset is too large for MongoDB.")
                return

            self.repository.upload_dataset(name=path.stem, session_id=self.session.session_id, uploaded_by=self.username,records=records)

            self.refresh_datasets()
            sg.popup("Dataset uploaded successfully.")

        except (OSError, ValueError, TypeError) as error:
            sg.popup_error(f"Upload failed: {error}")
        except Exception as error:
            sg.popup_error(f"Database error: {error}")

    def load_dataset(self, values):
        selected = values["-DATASETS-"]

        if not selected:
            sg.popup_error("Please select a dataset.")
            return

        selected_index = self.view.window[
            "-DATASETS-"
        ].get_indexes()[0]

        selected_dataset = self.datasets[selected_index]

        dataset = self.repository.find_by_id(selected_dataset.dataset_id, self.session.session_id)

        if dataset is None:
            sg.popup_error("Dataset could not be found.")
            return

        if not self.visualiser.load_data(dataset.records):
            sg.popup_error("Unable to load remote dataset.")
            return

        columns = list(dataset.records[0].keys())

        x_column = sg.popup_get_text(
            f"Available columns: {', '.join(columns)}\n"
            "Enter the X-axis column:"
        )

        if x_column is None:
            return

        y_column = sg.popup_get_text(
            f"Available columns: {', '.join(columns)}\n"
            "Enter the Y-axis column:"
        )

        if y_column is None:
            return

        if x_column not in columns or y_column not in columns:
            sg.popup_error("Invalid graph column selection.")
            return

        try:
            figure = self.visualiser.create_line_chart(x_column, y_column, dataset.name)

            if figure is None:
                sg.popup_error("Unable to create graph.")
                return

            import matplotlib.pyplot as plt
            plt.show()
            plt.close(figure)

        except (ValueError, TypeError, KeyError) as error:
            sg.popup_error(f"Graph error: {error}")

    def run(self):
        try:
            self.refresh_datasets()

            while True:
                event, values = self.view.read()

                if event in (sg.WIN_CLOSED, "Continue to Chat"):
                    break

                if event == "Refresh":
                    self.refresh_datasets()

                elif event == "Upload CSV":
                    self.upload_csv()

                elif event == "Load Dataset":
                    self.load_dataset(values)

        finally:
            self.view.close()