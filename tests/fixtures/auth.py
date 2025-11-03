import allure
import mimesis
import pytest

from tests.clients.oauth_client import OAuthClient
from tests.models.config import Envs

person = mimesis.Person()

@pytest.fixture(scope="session")
def auth_client(envs: Envs):
    return OAuthClient(envs)


@pytest.fixture(scope="module")
def auth_token(request, envs: Envs, user_data, auth_client):
    def get_auth_token(user):
        module_name = request.node.module.__name__
        if 'test_api' in module_name:
            user = user_data.get_user(1)
        elif 'test_db' in module_name:
            user = user_data.get_user(2)
        else:
            if user is None:
                user = user_data.get_user(0)
        return  auth_client.get_token(user['login'], user['password'], envs)

    return get_auth_token


@pytest.fixture
def sign_up(auth_client, envs):
    def sign_up(user=None):
        if user is None:
            user = {'login': 'aboba', 'password': '12345'}
        resp = auth_client.register(user['login'], user['password'], envs)
        assert resp.status_code == 201, 'Регистрация завершилась неуспешно'
        return resp

    return sign_up


@pytest.fixture
def sign_in(users_from_db, auth_client, envs, sign_up):
    def sign_in(user):
        with allure.step("Подготовка данных"):
            if not any(user['login'].lower() == u.username.lower() for u in users_from_db()):
                sign_up(user)
        with allure.step("Авторизация"):
            resp = auth_client.get_token(user['login'], user['password'], envs)
            return resp

    return sign_in


@pytest.fixture
def sign_up_many_users(auth_client, envs):
    def sign_up(count):
        users = []
        for i in range(count):
            login = person.username()
            resp = auth_client.register(login, person.password(), envs)
            assert resp.status_code == 201, 'Регистрация завершилась неуспешно'
            users.append(login)
        return tuple(users)

    return sign_up