import argparse
import sys


class App:
    def __init__(self):
        from data.user_repository import UserRepository
        from data.message_repository import MessageRepository
        from data.session_repository import SessionRepository
        from data.dataset_repository import DatasetRepository

        self.user_repository = UserRepository()
        self.message_repository = MessageRepository()
        self.session_repository = SessionRepository()
        self.dataset_repository = DatasetRepository()

    def run(self, session_id=None):
        """Authenticate and launch the remote DES workspace."""
        from controller.login_controller import LoginController
        from controller.workspace_controller import WorkspaceController

        user = LoginController(self.user_repository).run()

        if not user:
            return

        workspace = WorkspaceController(
            user.name,
            self.session_repository,
            self.dataset_repository,
            self.message_repository,
            initial_session_id=session_id,
        )
        workspace.run()


def run_local(file_name=None):
    """Launch Local Mode with an optional CSV file."""
    from local_gui import LocalGUI

    gui = LocalGUI()

    if file_name is not None:
        gui.load_csv(file_name)

    gui.run()


def run_remote(session_id=None):
    """Launch Remote Mode with an optional DES session."""
    App().run(session_id=session_id)


def run_tests(verbose=False, pattern="test_*.py"):
    """Run headless automated tests."""
    import unittest

    suite = unittest.defaultTestLoader.discover(
        start_dir="tests", pattern=pattern
    )

    verbosity = 2 if verbose else 1

    result = unittest.TextTestRunner(
        verbosity=verbosity,
    ).run(suite)

    return 0 if result.wasSuccessful() else 1


def main():
    """Parse command-line arguments and launch the selected mode."""
    parser = argparse.ArgumentParser(
        description="SDV602 Data Exploration System"
    )

    subparsers = parser.add_subparsers(
        dest="mode", help="Select an application mode"
    )

    local_parser = subparsers.add_parser(
        "local", help="Launch the local CSV explorer"
    )
    local_parser.add_argument(
        "--file", help="CSV file to load when starting Local Mode"
    )

    remote_parser = subparsers.add_parser(
        "remote", help="Launch the remote DES workspace"
    )
    remote_parser.add_argument(
        "--session", help="DES session ID to open after login"
    )

    test_parser = subparsers.add_parser(
        "test", help="Run automated tests without opening the GUI"
    )
    test_parser.add_argument(
        "--verbose", action="store_true", help="Display detailed test results"
    )
    test_parser.add_argument(
        "--pattern", default="test_*.py", help="Test filename pattern"
    )

    args = parser.parse_args()

    if args.mode == "local":
        run_local(file_name=args.file)

    elif args.mode == "remote" or args.mode is None:
        session_id = args.session if args.mode == "remote" else None
        run_remote(session_id=session_id)

    elif args.mode == "test":
        return run_tests(verbose=args.verbose, pattern=args.pattern)
    return 0


if __name__ == "__main__":
    sys.exit(main())
