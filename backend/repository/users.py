from fastapi import Depends
from sqlmodel import Session, select

from backend.models.users import User
from backend.repository.database import get_session


class UserRepo:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def get_by_id(self, user_id: int):
        return self.session.get(User, user_id)

    def get_by_username(self, username: str):
        return self.session.exec(
            select(User).where(User.username == username)
        ).one_or_none()
