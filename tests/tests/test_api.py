import random

import allure
import mimesis
from faker.proxy import Faker

from tests.utils.constants import currencies_api
from tests.models.profile import ProfilePayload
from tests.models.spend import Category, SpendAdd, SpendSearchPayload
from tests.utils.helpers import sign_in


person = mimesis.Person()
num = mimesis.Numeric()
faker = Faker()

@allure.epic("API")
class TestAPI:
    @allure.feature("Профиль")
    @allure.story("Изменение информации о пользователе")
    def test_update_user(self, users_from_db, spends_client, user_data, auth_client, envs):
        user = user_data.get_user(1)
        sign_in(user, users_from_db(), auth_client, envs)
        name = person.name()
        user_db_id = next(us.id for us in users_from_db() if us.username == user['login'])
        payload = ProfilePayload(fullname=name,
                                 id=str(user_db_id),
                                 username=user['login'])
        resp = spends_client(user).edit_profile(payload)
        assert resp.fullname == payload.fullname and resp.username == payload.username

    @allure.feature("Категории")
    @allure.story("Добавление валидной категории")
    def test_add_category(self, user_data, users_from_db, spends_client, auth_client, envs):
        user = user_data.get_user(1)
        sign_in(user, users_from_db(), auth_client, envs)
        category = mimesis.Text('en').word()
        resp = spends_client(user).add_category(category)
        assert resp.name == category and resp.username == user['login'] and not resp.archived
        user_data.add_category(user_id=1, category=category)

    @allure.feature("Категории")
    @allure.story("Добавление невалидной категории")
    def test_add_invalid_category(self, user_data, users_from_db, spends_client, auth_client, envs):
        user = user_data.get_user(1)
        sign_in(user, users_from_db(), auth_client, envs)
        category = '+'
        resp = spends_client(user).add_category(category, expect_error=True)
        assert resp.status_code == 400

    @allure.feature("Категории")
    @allure.story("Изменение категории")
    def test_update_category(self, user_data, spends_client, categories, users_from_db, auth_client, envs, add_category_api):
        user = user_data.get_user(1)
        sign_in(user, users_from_db(), auth_client, envs)
        cat_name = mimesis.Text('en').word()
        new_category = mimesis.Text('en').word()
        add_category_api(user, cat_name)
        user_data.add_category(user_id=1, category=cat_name)
        category = next((cat for cat in categories(user) if cat.name == cat_name), None)
        payload = Category(name=new_category,
                           username=user['login'],
                           archived=False,
                           id=category.id)
        resp = spends_client(user).edit_category(payload)
        assert resp.name == new_category and resp.username == user['login']
        user_data.remove_category(user_id=1, category=cat_name)
        user_data.add_category(user_id=2, category=new_category)

    @allure.feature("Категории")
    @allure.story("Архивирование категории")
    def test_archive_category(self, user_data, spends_client, categories, users_from_db, auth_client, envs, add_category_api):
        user = user_data.get_user(1)
        sign_in(user, users_from_db(), auth_client, envs)
        cat_name = mimesis.Text('en').word()
        add_category_api(user, cat_name)
        user_data.add_category(user_id=1, category=cat_name)
        category = next((cat for cat in categories(user) if cat.name == cat_name), None)
        payload = Category(name=category.name,
                           username=user['login'],
                           archived=True,
                           id=category.id)
        resp = spends_client(user).edit_category(payload)
        assert not any(resp.name == cat.name for cat in categories(user))
        user_data.remove_category(user_id=1, category=category.name)

    @allure.feature("Траты")
    @allure.story("Добавление валидной траты")
    def test_add_spend(self, user_data, spends_client, users_from_db, auth_client, envs):
        user = user_data.get_user(1)
        sign_in(user, users_from_db(), auth_client, envs)
        category_name = mimesis.Text('en').word()
        random_date = faker.date_time_this_decade().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        payload = SpendAdd(amount=num.float_number(1, 100000),
                           description=mimesis.Text('en').word(),
                           category={'name': category_name},
                           spendDate=random_date,
                           currency=random.choice(currencies_api))
        resp = spends_client(user).add_spend(payload)
        assert resp.category.name == category_name and resp.description == payload.description
        user_data.add_spending(user_id=1, spending=category_name)

    @allure.feature("Траты")
    @allure.story("Добавление невалидной траты")
    def test_add_invalid_spend(self, user_data, spends_client, users_from_db, auth_client, envs):
        user = user_data.get_user(1)
        sign_in(user, users_from_db(), auth_client, envs)
        category_name = 'a'
        random_date = faker.date_time_this_decade().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        payload = SpendAdd(amount=-10.0,
                           description=mimesis.Text('en').word(),
                           category={'name': category_name},
                           spendDate=random_date,
                           currency=random.choice(currencies_api))
        resp = spends_client(user).add_spend(payload, expect_error=True)
        assert resp.status_code == 400

    @allure.feature("Траты")
    @allure.story("Изменение траты")
    def test_edit_spend(self, user_data, spends_client, spends, users_from_db, auth_client, envs):
        user = user_data.get_user(1)
        sign_in(user, users_from_db(), auth_client, envs)
        spend = random.choice(spends(user))
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
        resp = spends_client(user).edit_spend(payload)
        assert resp.category.name == category_name and resp.description == payload.description and resp.amount == amount
        user_data.remove_spending(user_id=1, spending=spend['category']['name'])
        user_data.add_spending(user_id=1, spending=category_name)

    @allure.feature("Траты")
    @allure.story("Поиск траты")
    def test_search_spend(self, user_data, spends_client, spends, users_from_db, auth_client, envs):
        user = user_data.get_user(1)
        sign_in(user, users_from_db(), auth_client, envs)
        spend = random.choice(spends(user))
        payload = SpendSearchPayload(page=0,
                                     searchQuery=spend['category']['name'])
        resp = spends_client(user).search_spend(payload)
        assert resp.numberOfElements == 1 and resp.content[0].category.name == spend['category']['name']

    @allure.feature("Траты")
    @allure.story("Удаление всех трат")
    def test_delete_all_spends(self, user_data, spends_client, spends, users_from_db, auth_client, envs):
        user = user_data.get_user(1)
        ids = [str(spend['id']) for spend in spends(user)]
        sign_in_res = sign_in(user, users_from_db(), auth_client, envs)
        resp = spends_client(user).remove_spends(ids)
        assert resp.status_code == 200
        user_data.remove_all_spendings(user_id=1)
