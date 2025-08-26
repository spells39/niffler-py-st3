import random

import allure
import mimesis
from faker.proxy import Faker

from tests.constants import currencies_api
from tests.models.profile import ProfilePayload
from tests.models.spend import Category, SpendAdd, SpendSearchPayload


person = mimesis.Person()
num = mimesis.Numeric()
faker = Faker()

class TestAPI:
    @allure.epic("API")
    @allure.feature("Профиль")
    @allure.story("Изменение информации о пользователе")
    def test_update_user(self, sign_in, users_from_db, spends_client):
        user = sign_in[1]
        name = person.name()
        user_db_id = next(us.id for us in users_from_db() if us.username == user['login'])
        payload = ProfilePayload(fullname=name,
                                 id=str(user_db_id),
                                 username=user['login'])
        resp = spends_client.edit_profile(payload)
        assert resp.fullname == payload.fullname and resp.username == payload.username

    @allure.epic("API")
    @allure.feature("Категории")
    @allure.story("Добавление валидной категории")
    def test_add_category(self, sign_in, users_from_db, spends_client):
        user = sign_in[1]
        category = mimesis.Text('en').word()
        resp = spends_client.add_category(category)
        assert resp.name == category and resp.username == user['login'] and not resp.archived

    @allure.epic("API")
    @allure.feature("Категории")
    @allure.story("Добавление невалидной категории")
    def test_add_invalid_category(self, sign_in, users_from_db, spends_client):
        category = '+'
        resp = spends_client.add_category(category, expect_error=True)
        assert resp.status_code == 400

    @allure.epic("API")
    @allure.feature("Категории")
    @allure.story("Изменение категории")
    def test_update_category(self, sign_in, spends_client, categories):
        user = sign_in[1]
        new_category = mimesis.Text('en').word()
        category = random.choice(categories())
        payload = Category(name=new_category,
                           username=user['login'],
                           archived=False,
                           id=category.id)
        resp = spends_client.edit_category(payload)
        assert resp.name == new_category and resp.username == user['login']

    @allure.epic("API")
    @allure.feature("Категории")
    @allure.story("Архивирование категории")
    def test_archive_category(self, sign_in, spends_client, categories):
        category = random.choice(categories())
        payload = Category(name=category.name,
                           username=sign_in[1]['login'],
                           archived=True,
                           id=category.id)
        resp = spends_client.edit_category(payload)
        assert not any(resp.name == cat.name for cat in categories())

    @allure.epic("API")
    @allure.feature("Траты")
    @allure.story("Добавление валидной траты")
    def test_add_spend(self, sign_in, spends_client):
        category_name = mimesis.Text('en').word()
        random_date = faker.date_time_this_decade().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        payload = SpendAdd(amount=num.float_number(1, 100000),
                           description=mimesis.Text('en').word(),
                           category={'name': category_name},
                           spendDate=random_date,
                           currency=random.choice(currencies_api))
        resp = spends_client.add_spend(payload)
        assert resp.category.name == category_name and resp.description == payload.description

    @allure.epic("API")
    @allure.feature("Траты")
    @allure.story("Добавление невалидной траты")
    def test_add_invalid_spend(self, sign_in, spends_client):
        category_name = 'a'
        random_date = faker.date_time_this_decade().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        payload = SpendAdd(amount=-10.0,
                           description=mimesis.Text('en').word(),
                           category={'name': category_name},
                           spendDate=random_date,
                           currency=random.choice(currencies_api))
        resp = spends_client.add_spend(payload, expect_error=True)
        assert resp.status_code == 400

    @allure.epic("API")
    @allure.feature("Траты")
    @allure.story("Изменение траты")
    def test_edit_spend(self, sign_in, spends_client, spends):
        spend = random.choice(spends())
        category_name = mimesis.Text('en').word()
        amount = num.float_number(1, 100000)
        desc = mimesis.Text('en').word()
        random_date = faker.date_time_this_decade().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        payload = SpendAdd(amount=amount,
                           description=desc,
                           category={'name': category_name},
                           spendDate=random_date,
                           currency=spend['currency'],
                           id=spend['id'])
        resp = spends_client.edit_spend(payload)
        assert resp.category.name == category_name and resp.description == payload.description and resp.amount == amount

    @allure.epic("API")
    @allure.feature("Траты")
    @allure.story("Поиск траты")
    def test_search_spend(self, sign_in, spends_client, spends):
        spend = random.choice(spends())
        payload = SpendSearchPayload(page=0,
                                     searchQuery=spend['category']['name'])
        resp = spends_client.search_spend(payload)
        assert resp.numberOfElements == 1 and resp.content[0].category.name == spend['category']['name']

    @allure.epic("API")
    @allure.feature("Траты")
    @allure.story("Удаление всех трат")
    def test_delete_all_spends(self, sign_in, spends_client, spends):
        ids = [str(spend['id']) for spend in spends()]
        resp = spends_client.remove_spends(ids)
        assert resp.status_code == 200
