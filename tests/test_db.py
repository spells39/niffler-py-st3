# 1. через апи добавить трату, проверить в бд, есть ли она _______DONE
# 2. через апи редактировать трату, проверить в бд _______DONE
# 3. через апи удалить трату, проверить в бд _______DONE
# 4. через апи добавить категорию, проверить в бд _______DONE
# 5. через апи редактировать категорию, проверить в бд _______DONE
# 6. через бд удалить категорию и проверить фронт/бек _______DONE
import os
import random

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

    def test_add_category(self, sign_in, api_url):
        client = SpendsHttpClient(base_url=api_url, token=sign_in[0])
        category = mimesis.Text('en').word()
        resp = client.add_category(category)
        db_client = SpendDb(db_url)
        db_cat = db_client.get_category_by_id(resp.id)
        assert db_cat.name == category and db_cat.id == resp.id

    def test_edit_category(self, sign_in, api_url, categories):
        client = SpendsHttpClient(base_url=api_url, token=sign_in[0])
        category = random.choice(categories())
        category.name = mimesis.Text('en').word()
        resp = client.edit_category(category)
        db_client = SpendDb(db_url)
        db_cat = db_client.get_category_by_id(resp.id)
        assert db_cat.name == category.name and db_cat.id == resp.id

    def test_remove_category(self, sign_in, api_url, categories):
        db_client = SpendDb(db_url)
        db_categories = db_client.get_categories(sign_in[1]['login'])
        db_category = random.choice(db_categories)
        while db_category.archived:
            db_category = random.choice(db_categories)
        db_client.remove_category_by_id(db_category.id)
        assert not any(db_category.id in cat.id for cat in categories())

    def test_add_spend(self, sign_in, api_url):
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
        db_client = SpendDb(db_url)
        db_spend = db_client.get_spend_by_id(resp.id)
        assert db_spend.amount == amount and db_spend.description == description

    def test_edit_spend(self, sign_in, api_url, spends):
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
        db_client = SpendDb(db_url)
        db_spend = db_client.get_spend_by_id(spend['id'])
        assert db_spend.amount == amount and db_spend.description == description

    def test_remove_spend(self, sign_in, spends):
        spend = random.choice(spends())
        db_client = SpendDb(db_url)
        db_client.remove_spend(spend['id'])
        assert not any(spend['id'] in sp['id'] for sp in spends())

