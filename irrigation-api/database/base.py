from abc import ABC, abstractmethod


class BaseUserRepository(ABC):
    @abstractmethod
    def get_user_by_username(self, username: str):
        pass

    @abstractmethod
    def create_user(self, username: str, hashed_pwd: str):
        pass
