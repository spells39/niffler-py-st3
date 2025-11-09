import random

import mimesis
import pytest
from faker.proxy import Faker

from tests.clients.spends_client import SpendsHttpClient
from tests.database.auth_db import AuthDb
from tests.database.spend_db import SpendDb
from tests.database.userdata_db import UserdataDb
from tests.models.spend import SpendAdd
from tests.utils.constants import currencies_api
from tests.utils.helpers import sign_in

faker = Faker()
num = mimesis.Numeric()

@pytest.fixture
def spends_client(envs, auth_token):# -> SpendsHttpClient:

    def get_spends_client(user):
        return SpendsHttpClient(envs, auth_token(user))

    return get_spends_client

@pytest.fixture
def spend_db(envs) -> SpendDb:
    return SpendDb(envs)

@pytest.fixture
def auth_db(envs) -> AuthDb:
    return AuthDb(envs.auth_db_url)

@pytest.fixture
def userdata_db(envs) -> UserdataDb:
    return UserdataDb(envs.userdata_db_url)


@pytest.fixture
def users_from_db(auth_db):
    def get_users():
        return auth_db.get_users()

    return get_users


@pytest.fixture
def categories(request, spends_client, users_from_db, auth_client, envs):
    def get_categories(user):
        sign_in(user, users_from_db(), auth_client, envs)
        categories = spends_client(user).get_categories()
        return categories

    return get_categories


@pytest.fixture
def spends(request, spends_client, users_from_db, auth_client, envs):
    def get_spends(user):
        sign_in(user, users_from_db(), auth_client, envs)
        spends = spends_client(user).get_spends()
        return spends

    return get_spends


@pytest.fixture
def add_category_api(spends_client, users_from_db, auth_client, envs):
    def add_category(user, category):
        sign_in(user, users_from_db(), auth_client, envs)
        resp = spends_client(user).add_category(category)
        return resp

    return add_category

@pytest.fixture
def add_spend_api(spends_client, users_from_db, auth_client, envs):
    def add_spend(user, category):
        sign_in(user, users_from_db(), auth_client, envs)
        random_date = faker.date_time_this_decade().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        payload = SpendAdd(amount=num.float_number(1, 100000),
                           description=mimesis.Text('en').word(),
                           category={'name': category},
                           spendDate=random_date,
                           currency=random.choice(currencies_api))
        resp = spends_client(user).add_spend(payload)
        return resp

    return add_spend


@pytest.fixture
def add_random_spends_api(spends_client, users_from_db, auth_client, envs):
    def random_spends(user):
        for _ in range(random.randint(1, 5)):
            sign_in(user, users_from_db(), auth_client, envs)
            category = mimesis.Text('en').word()
            random_date = faker.date_time_this_decade().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            payload = SpendAdd(amount=num.float_number(1, 100000),
                               description=mimesis.Text('en').word(),
                               category={'name': category},
                               spendDate=random_date,
                               currency=random.choice(currencies_api))
            resp = spends_client(user).add_spend(payload)

    return random_spends