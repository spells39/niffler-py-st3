import os
import random

import allure
import faker
import mimesis
from dotenv import load_dotenv

from tests.clients.spends_client import SpendsHttpClient
from tests.constants import currencies_api
from tests.database.spend_db import SpendDb
from tests.models.spend import SpendAdd

load_dotenv()

db_url = os.getenv("SPEND_DB_URL")
num = mimesis.Numeric()
faker = faker.Faker()


class TestDB:

    @allure.epic("Профиль")
    @allure.feature("Работа с БД")
    @allure.story("Добавление категории")
    def test_add_category(self, sign_in, api_url):
        with allure.step("Добавление категории"):
            client = SpendsHttpClient(base_url=api_url, token=sign_in[0])
            category = mimesis.Text('en').word()
            resp = client.add_category(category)
        with allure.step("Проверка наличия категории в БД"):
            db_client = SpendDb(db_url)
            db_cat = db_client.get_category_by_id(resp.id)
            assert db_cat.name == category and db_cat.id == resp.id

    @allure.epic("Профиль")
    @allure.feature("Работа с БД")
    @allure.story("Редактирование категории")
    def test_edit_category(self, sign_in, api_url, categories):
        with allure.step("Редактирование категории"):
            client = SpendsHttpClient(base_url=api_url, token=sign_in[0])
            category = random.choice(categories())
            category.name = mimesis.Text('en').word()
            resp = client.edit_category(category)
        with allure.step("Проверка наличия категории в БД"):
            db_client = SpendDb(db_url)
            db_cat = db_client.get_category_by_id(resp.id)
            assert db_cat.name == category.name and db_cat.id == resp.id

    @allure.epic("Профиль")
    @allure.feature("Работа с БД")
    @allure.story("Удаление категории")
    def test_remove_category(self, sign_in, api_url, categories):
        with allure.step("Удаление категории из БД"):
            db_client = SpendDb(db_url)
            db_categories = db_client.get_categories(sign_in[1]['login'])
            db_category = random.choice(db_categories)
            while db_category.archived:
                db_category = random.choice(db_categories)
            db_client.remove_category_by_id(db_category.id)
        with allure.step("Проверка удаления категории"):
            assert not any(db_category.id in cat.id for cat in categories())

    @allure.epic("Главная страница")
    @allure.feature("Работа с БД")
    @allure.story("Добавление траты")
    def test_add_spend(self, sign_in, api_url):
        with allure.step("Добавление траты"):
            client = SpendsHttpClient(base_url=api_url, token=sign_in[0])
            category = mimesis.Text('en').word()
            description = mimesis.Text('en').word()
            amount = num.float_number(1, 110000)
            random_date = faker.date_time_this_decade().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            spend = SpendAdd(amount=amount,
                             description=description,
                             category={'name': category},
                             spendDate=random_date,
                             currency=random.choice(currencies_api))
            resp = client.add_spend(spend)
        with allure.step("Проверка наличия траты в БД"):
            db_client = SpendDb(db_url)
            db_spend = db_client.get_spend_by_id(resp.id)
            assert db_spend.amount == amount and db_spend.description == description

    @allure.epic("Главная страница")
    @allure.feature("Работа с БД")
    @allure.story("Редактирование траты")
    def test_edit_spend(self, sign_in, api_url, spends):
        with allure.step("Редактирование траты"):
            client = SpendsHttpClient(base_url=api_url, token=sign_in[0])
            category = mimesis.Text('en').word()
            description = mimesis.Text('en').word()
            amount = num.float_number(1, 100000)
            random_date = faker.date_time_this_decade().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            spend = random.choice(spends())
            payload = SpendAdd(amount=amount,
                               description=description,
                               category={'name': category},
                               spendDate=random_date,
                               currency=random.choice(currencies_api),
                               id=spend['id'])
            resp = client.edit_spend(payload)
        with allure.step("Проверка наличия траты в БД"):
            db_client = SpendDb(db_url)
            db_spend = db_client.get_spend_by_id(spend['id'])
            assert db_spend.amount == amount and db_spend.description == description

    @allure.epic("Главная страница")
    @allure.feature("Работа с БД")
    @allure.story("Удаление траты")
    def test_remove_spend(self, sign_in, spends):
        with allure.step("Удаление траты"):
            spend = random.choice(spends())
            db_client = SpendDb(db_url)
            db_client.remove_spend(spend['id'])
        with allure.step("Проверка удаления траты"):
            assert not any(spend['id'] in sp['id'] for sp in spends())

