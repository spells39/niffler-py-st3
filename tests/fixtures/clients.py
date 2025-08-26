import pytest

from tests.clients.spends_client import SpendsHttpClient
from tests.database.auth_db import AuthDb
from tests.database.spend_db import SpendDb


@pytest.fixture
def spends_client(envs, auth_token) -> SpendsHttpClient:
    return SpendsHttpClient(envs, auth_token)

@pytest.fixture
def spend_db(envs) -> SpendDb:
    return SpendDb(envs)

@pytest.fixture
def auth_db(envs) -> AuthDb:
    return AuthDb(envs.auth_db_url)


@pytest.fixture
def users_from_db(auth_db):
    def get_users():
        return auth_db.get_users()

    return get_users


@pytest.fixture
def categories(request, spends_client, spend_db, sign_in):
    def get_categories():
        categories = spends_client.get_categories()
        return categories

    return get_categories


@pytest.fixture
def spends(request, spends_client, spend_db, sign_in):
    def get_spends():
        spends = spends_client.get_spends()
        return spends

    return get_spends