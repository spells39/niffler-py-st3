from sqlalchemy import Engine, create_engine, Sequence
from sqlmodel import Session, select

from tests.models.oauth import User


class AuthDb:
    engine: Engine

    def __init__(self, auth_url: str):
        self.engine = create_engine(auth_url)

    def get_users(self) -> Sequence[User]:
        with Session(self.engine) as session:
            statement = select(User)
            return session.exec(statement).all()

    def get_user_by_id(self, user_id) -> User:
        with Session(self.engine) as session:
            statement = select(User).where(User.id == user_id)
            return session.exec(statement).first()

    def get_user_by_username(self, username: str) -> User:
        with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            return session.exec(statement).first()