import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import FreeSimpleGUI as sg  # noqa: E402

from view.des_view import DesView  # noqa: E402


def main():
    view = DesView(session_name="Test Session", username="Luke")

    try:
        while True:
            event, values = view.read(timeout=100)

            if event in (sg.WIN_CLOSED, "Close DES"):
                break

            if event == "Manage Data Sources":
                sg.popup("Dataset manager will be connected next.")

            elif event == "Refresh Chat":
                sg.popup("Chat refresh will be connected next.")

            elif event == "Send":
                message = values["-CHAT-"].strip()

                if message:
                    sg.popup(f"Test message: {message}")
                    view.clear_input()

    finally:
        view.close()


if __name__ == "__main__":
    main()
