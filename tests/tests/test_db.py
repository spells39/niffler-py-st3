import os
import random

import allure
import faker
import mimesis
from dotenv import load_dotenv

from tests.clients.spends_client import SpendsHttpClient
from tests.utils.constants import currencies_api
from tests.database.spend_db import SpendDb
from tests.models.spend import SpendAdd
from tests.utils.helpers import sign_in

load_dotenv()

db_url = os.getenv("SPEND_DB_URL")
num = mimesis.Numeric()
faker = faker.Faker()


class TestDB:

    @allure.epic("Профиль")
    @allure.feature("Работа с БД")
    @allure.story("Добавление категории")
    def test_add_category(self, user_data, api_url, envs, users_from_db, auth_client):
        with allure.step("Добавление категории"):
            user = user_data.get_user(2)
            sign_in_res = sign_in(user, users_from_db(), auth_client, envs)
            client = SpendsHttpClient(envs, token=sign_in_res)
            category = mimesis.Text('en').word()
            resp = client.add_category(category)
        with allure.step("Проверка наличия категории в БД"):
            db_client = SpendDb(envs)
            db_cat = db_client.get_category_by_id(resp.id)
            assert db_cat.name == category and db_cat.id == resp.id
            user_data.add_category(user_id=2, category=category)

    @allure.epic("Профиль")
    @allure.feature("Работа с БД")
    @allure.story("Редактирование категории")
    def test_edit_category(self, user_data, api_url, categories, envs, users_from_db, auth_client, base_url):
        with allure.step("Редактирование категории"):
            user = user_data.get_user(2)
            sign_in_res = sign_in(user, users_from_db(), auth_client, envs)
            client = SpendsHttpClient(envs, token=sign_in_res)
            cat_name = mimesis.Text('en').word()
            client.add_category(cat_name)
            user_data.add_category(user_id=2, category=cat_name)
            cats = categories(user)
            category = next((cat for cat in categories(user) if cat.name == cat_name), None)
            category.name = mimesis.Text('en').word()
            resp = client.edit_category(category)
        with allure.step("Проверка наличия категории в БД"):
            db_client = SpendDb(envs)
            db_cat = db_client.get_category_by_id(resp.id)
            assert db_cat.name == category.name and db_cat.id == resp.id
            user_data.remove_category(user_id=2, category=cat_name)
            user_data.add_category(user_id=2, category=category.name)

    @allure.epic("Профиль")
    @allure.feature("Работа с БД")
    @allure.story("Удаление категории")
    def test_remove_category(self, user_data, api_url, categories, envs, users_from_db, auth_client, base_url):
        with allure.step("Удаление категории из БД"):
            user = user_data.get_user(2)
            cat_name = mimesis.Text('en').word()
            sign_in_res = sign_in(user, users_from_db(), auth_client, envs)
            client = SpendsHttpClient(envs, token=sign_in_res)
            client.add_category(cat_name)
            user_data.add_category(user_id=2, category=cat_name)
            db_client = SpendDb(envs)
            db_categories = db_client.get_categories(user['login'])
            db_category = random.choice(db_categories)
            while db_category.archived:
                db_category = random.choice(db_categories)
            db_client.remove_category_by_id(db_category.id)
        with allure.step("Проверка удаления категории"):
            cats=categories(user)
            assert not any(db_category.id == cat.id for cat in categories(user))
            user_data.remove_category(user_id=2, category=cat_name)

    @allure.epic("Главная страница")
    @allure.feature("Работа с БД")
    @allure.story("Добавление траты")
    def test_add_spend(self, user_data, api_url, envs, users_from_db, auth_client):
        with allure.step("Добавление траты"):
            user = user_data.get_user(2)
            sign_in_res = sign_in(user, users_from_db(), auth_client, envs)
            client = SpendsHttpClient(envs, token=sign_in_res)
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
            db_client = SpendDb(envs)
            db_spend = db_client.get_spend_by_id(resp.id)
            assert db_spend.amount == amount and db_spend.description == description
            user_data.add_spending(user_id=2, spending=category)

    @allure.epic("Главная страница")
    @allure.feature("Работа с БД")
    @allure.story("Редактирование траты")
    def test_edit_spend(self, user_data, api_url, spends, envs, users_from_db, auth_client):
        with allure.step("Редактирование траты"):
            user = user_data.get_user(2)
            sign_in_res = sign_in(user, users_from_db(), auth_client, envs)
            client = SpendsHttpClient(envs, token=sign_in_res)
            category = mimesis.Text('en').word()
            description = mimesis.Text('en').word()
            amount = num.float_number(1, 100000)
            random_date = faker.date_time_this_decade().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            spend = random.choice(spends(user))
            payload = SpendAdd(amount=amount,
                               description=description,
                               category={'name': category},
                               spendDate=random_date,
                               currency=random.choice(currencies_api),
                               id=spend['id'])
            resp = client.edit_spend(payload)
        with allure.step("Проверка наличия траты в БД"):
            db_client = SpendDb(envs)
            db_spend = db_client.get_spend_by_id(spend['id'])
            assert db_spend.amount == amount and db_spend.description == description
            user_data.remove_spending(user_id=2, spending=spend['category']['name'])
            user_data.add_spending(user_id=2, spending=category)

    @allure.epic("Главная страница")
    @allure.feature("Работа с БД")
    @allure.story("Удаление траты")
    def test_remove_spend(self, user_data, spends, envs, users_from_db):
        with allure.step("Удаление траты"):
            user = user_data.get_user(2)
            spend = random.choice(spends(user))
            db_client = SpendDb(envs)
            db_client.remove_spend(spend['id'])
        with allure.step("Проверка удаления траты"):
            assert not any(spend['id'] in sp['id'] for sp in spends(user))
            user_data.remove_spending(user_id=2, spending=spend['category']['name'])

