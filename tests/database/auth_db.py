from sqlalchemy import Engine, create_engine, Sequence
from sqlmodel import Session, select

from tests.models.spend import User

class AuthDb:
    engine: Engine

    def __init__(self, auth_url: str):
        self.engine = create_engine(auth_url)

    def get_users(self) -> Sequence[User]:
        with Session(self.engine) as session:
            statement = select(User)
            return session.exec(statement).all()