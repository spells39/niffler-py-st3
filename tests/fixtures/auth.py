import pytest

from tests.clients.oauth_client import OAuthClient
from tests.models.config import Envs


@pytest.fixture(scope="session")
def auth_token(envs: Envs, users):
    return  OAuthClient(envs).get_token(users[0]['login'], users[0]['password'], envs)