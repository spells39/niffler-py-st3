import allure
from allure_commons.types import AttachmentType
from sqlalchemy import Engine, create_engine, Sequence, event
from sqlmodel import Session, select

from tests.models.spend import Category, Spend


class SpendDb:
    engine: Engine

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        event.listen(self.engine, "do_execute", fn=self.attach_sql)

    @staticmethod
    def attach_sql(cursor, statement, parameters, context):
        statement_with_params = statement % parameters
        name = statement.split(" ")[0] + " " + context.engine.url.database
        allure.attach(statement_with_params, name=name, attachment_type=AttachmentType.TEXT)

    def get_categories(self, username: str) -> Sequence[Category]:
        with Session(self.engine) as session:
            statement = select(Category).where(Category.username == username)
            return session.exec(statement).all()

    def delete_category(self, category_id: str):
        with Session(self.engine) as session:
            category = session.get(Category, category_id)
            session.delete(category)
            session.commit()

    def get_category_by_id(self, cat_id):
        with Session(self.engine) as session:
            statement = select(Category).where(Category.id == cat_id)
            return session.exec(statement).first()

    def get_category_by_name(self, cat_name: str):
        with Session(self.engine) as session:
            statement = select(Category).where(Category.name == cat_name)
            return session.exec(statement).first()

    def remove_category_by_id(self, cat_id: int):
        with Session(self.engine) as session:
            category = session.get(Category, cat_id)
            session.delete(category)
            session.commit()

    def remove_category_by_name(self, cat_name: str):
        with Session(self.engine) as session:
            statement = select(Category).where(Category.name == cat_name)
            cat = session.exec(statement).first()
            if cat:
                session.delete(cat)
                session.commit()

    def get_spend_by_id(self, spend_id):
        with Session(self.engine) as session:
            statement = select(Spend).where(Spend.id == spend_id)
            return session.exec(statement).first()

    def remove_spend(self, id: int):
        with Session(self.engine) as session:
            spend = session.get(Spend, id)
            session.delete(spend)
            session.commit()