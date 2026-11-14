from data.user_repository import UserRepository
from data.message_repository import MessageRepository
from data.session_repository import SessionRepository
from data.dataset_repository import DatasetRepository

from controller.login_controller import LoginController
from controller.session_controller import SessionController
from controller.dataset_controller import DatasetController
from controller.chat_controller import ChatController



class App:
    def __init__(self):
        self.user_repository = UserRepository()
        self.message_repository = MessageRepository()
        self.session_repository = SessionRepository()
        self.dataset_repository = DatasetRepository()

    def run(self):
        user = LoginController(self.user_repository).run()

        if not user:
            return

        session = SessionController(
            user.name, 
            self.session_repository
        ).run()

        if not session:
            return
        
        DatasetController(
            user.name,
            session,
            self.dataset_repository,
        ).run()
        
        ChatController(
            user.name, 
            self.message_repository,
            session.session_id
        ).run()

if __name__ == "__main__":
    App().run()