import FreeSimpleGUI as sg
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure


class DesView:
    """Display an embedded graph and live chat in one DES window."""

    def __init__(self, session_name, username):
        sg.theme("DarkBlue3")

        self.session_name = session_name
        self.username = username
        self.figure_canvas = None
        self.toolbar = None
        self.figure = None

        graph_column = [
            [sg.Text("Data Visualisation", font=("Arial", 16))],
            [sg.Text("No dataset loaded", key="-DATASET-", size=(55, 1))],
            [sg.Canvas(key="-TOOLBAR-", size=(650, 40))],
            [sg.Canvas(key="-GRAPH-CANVAS-", size=(650, 400))],
            [sg.Text("Select a dataset to display its graph.", key="-DESCRIPTION-", size=(65, 3))],
        ]

        chat_column = [
            [sg.Text("Live Chat", font=("Arial", 16))],
            [sg.Multiline(size=(35, 22), disabled=True, autoscroll=True, key="-OUTPUT-")],
            [sg.Input(size=(27, 1), key="-CHAT-", do_not_clear=True), sg.Button("Send", bind_return_key=True)],
        ]

        layout = [
            [sg.Text(f"DES Session: {session_name}", font=("Arial", 20))],
            [sg.Text(f"Logged in as: {username}")],
            [sg.Button("Manage Data Sources"), sg.Button("Refresh Chat"), sg.Button("Close DES")],
            [sg.Column(graph_column, vertical_alignment="top"), sg.VSeparator(), sg.Column(chat_column, vertical_alignment="top")],
        ]

        self.window = sg.Window(f"SDV602 - DES - {session_name}", layout, finalize=True, resizable=True)
        self.show_placeholder()

    def display_figure(self, figure):
        """Embed a Matplotlib figure in the DES window."""
        self.clear_figure()
        self.figure = figure

        canvas = self.window["-GRAPH-CANVAS-"].TKCanvas

        self.figure_canvas = FigureCanvasTkAgg(figure, master=canvas)
        self.figure_canvas.draw()
        self.figure_canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        toolbar_canvas = self.window["-TOOLBAR-"].TKCanvas

        self.toolbar = NavigationToolbar2Tk(self.figure_canvas, toolbar_canvas, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side="top", fill="x")

    def clear_figure(self):
        """Remove the previous embedded figure and toolbar."""
        if self.toolbar is not None:
            self.toolbar.destroy()
            self.toolbar = None

        if self.figure_canvas is not None:
            self.figure_canvas.get_tk_widget().destroy()
            self.figure_canvas = None

        if self.figure is not None:
            plt.close(self.figure)
            self.figure = None

    def show_placeholder(self):
        """Display a placeholder chart before data is loaded."""
        figure = Figure(figsize=(7, 4))
        axes = figure.add_subplot(111)

        axes.set_title("Data Exploration System")
        axes.set_xlabel("X-axis")
        axes.set_ylabel("Y-axis")
        axes.text(0.5, 0.5, "No dataset loaded\nSelect Manage Data Sources", ha="center", va="center", transform=axes.transAxes, fontsize=12)

        figure.tight_layout()

        self.display_figure(figure)

    def update_graph(self, figure, dataset_name, description):
        """Replace the placeholder with the selected dataset graph."""
        self.display_figure(figure)
        self.window["-DATASET-"].update(f"Dataset: {dataset_name}")
        self.window["-DESCRIPTION-"].update(description)

    def update_messages(self, messages):
        """Display messages belonging to the current session."""
        output = ""

        for message in messages:
            output += f"{message.username}: {message.text}\n"

        self.window["-OUTPUT-"].update(output)

    def clear_input(self):
        """Clear the chat input after sending a message."""
        self.window["-CHAT-"].update("")

    def show_error(self, message):
        sg.popup_error(message)

    def read(self, timeout=None):
        return self.window.read(timeout=timeout)

    def close(self):
        self.clear_figure()
        self.window.close()
