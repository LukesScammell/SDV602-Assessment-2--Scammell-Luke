import FreeSimpleGUI as sg

from controller.chat_controller import ChatController
from controller.dataset_controller import DatasetController
from view.des_view import DesView


class DesController:
    """Coordinate the combined DES window, chat and datasets."""

    def __init__(
        self, username, session, message_repository, dataset_repository
    ):
        self.username = username
        self.session = session
        self.dataset_repository = dataset_repository

        self.view = DesView(session.name, username)

        self.chat = ChatController(
            username, message_repository, session.session_id, session.name
        )
        self.chat.attach_view(self.view)

        self.dataset_manager = None

    def start(self):
        """Start background chat polling."""
        self.chat.start()

    def process_results(self):
        """Update chat messages on the GUI thread."""
        self.chat.process_results()

    def update_graph(self, figure, dataset_name, description):
        """Display a selected dataset in the embedded graph."""
        self.view.update_graph(figure, dataset_name, description)

    def open_dataset_manager(self):
        """Open the dataset management window."""
        if self.dataset_manager is not None:
            sg.popup("The dataset manager is already open.")
            return

        manager = DatasetController(
            self.username,
            self.session,
            self.dataset_repository,
            graph_callback=self.update_graph,
        )

        try:
            manager.start()

        except Exception:
            manager.close()
            raise

        self.dataset_manager = manager

    def handle_event(self, event, values):
        """Handle events from the combined DES window."""
        if event == "Send":
            self.chat.handle_event(event, values)

        elif event == "Refresh Chat":
            self.chat.refresh_requested.set()

        elif event == "Manage Data Sources":
            self.open_dataset_manager()

    def handle_dataset_event(self, event, values):
        """Handle events from the dataset management window."""
        if self.dataset_manager is None:
            return

        if event in (sg.WIN_CLOSED, "Close"):
            self.close_dataset_manager()
        else:
            self.dataset_manager.handle_event(event, values)

    def close_dataset_manager(self):
        """Close the dataset manager without closing the DES."""
        if self.dataset_manager is not None:
            self.dataset_manager.close()
            self.dataset_manager = None

    def close(self):
        """Close the dataset manager, chat worker and DES window."""
        self.close_dataset_manager()
        self.chat.close()
        self.view.close()
