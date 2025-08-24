import os
from inspect import signature

import allure
import mimesis
import pytest
from allure_commons.reporter import AllureReporter
from allure_commons.types import AttachmentType
from allure_pytest.listener import AllureListener
from pytest import Item, FixtureDef, FixtureRequest
from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright

from tests.clients.auth_client import AuthClient
from tests.clients.spends_client import SpendsHttpClient
from tests.database.auth_db import AuthDb
from tests.database.spend_db import SpendDb
from tests.helpers import sign_up
from tests.models.config import Envs
from tests.pages.login import Login

person = mimesis.Person()


def allure_logger(config) -> AllureReporter:
    listener: AllureListener = config.pluginmanager.get_plugin("allure_listener")
    return listener.allure_logger


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_call(item: Item):
    yield
    allure.dynamic.title(" ".join(item.name.split("_")[1:]).title())


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_fixture_setup(fixturedef: FixtureDef, request: FixtureRequest):
    yield
    logger = allure_logger(request.config)
    item = logger.get_last_item()
    scope_letter = fixturedef.scope[0].upper()
    item.name = f"[{scope_letter}] " + " ".join(fixturedef.argname.split("_")).title()


@pytest.fixture(scope="session")
def envs():
    load_dotenv()
    env_instance =  Envs(
        front_url=os.getenv("BASE_URL"),
        api_url=os.getenv("API_URL"),
        spend_db_url=os.getenv("SPEND_DB_URL"),
        auth_db_url=os.getenv("USER_DB_URL"),
        test_username=os.getenv("TEST_USERNAME"),
        test_password=os.getenv("TEST_PASSWORD")
    )
    allure.attach(env_instance.model_dump_json(), name="envs", attachment_type=AttachmentType.JSON)
    return env_instance


@pytest.fixture(scope="session")
def base_url(envs):
    return os.getenv("BASE_URL")


@pytest.fixture(scope="session")
def api_url(envs):
    return os.getenv("API_URL")


@pytest.fixture(scope="session")
def auth_url(envs):
    return os.getenv("AUTH_URL")


@pytest.fixture(scope="function")
def open_page() -> Page:
    with sync_playwright() as sp:
        browser = sp.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        yield page
        browser.close()


@pytest.fixture
def spends_client(envs, sign_in) -> SpendsHttpClient:
    return SpendsHttpClient(envs.api_url, sign_in[0])

@pytest.fixture
def spend_db(envs) -> SpendDb:
    return SpendDb(envs.spend_db_url)

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


@pytest.fixture(scope="session", autouse=True)
def users():
    users = [{'login': 'aboba', 'password': '12345', 'categories': [], 'spendings': []}]
    for i in range(10):
        users.append({
            "login": person.username(),
            "password": person.password(),
            "categories": [],
            "spendings": []
        })
    yield users


@pytest.fixture(scope="session")
def auth_api_token(envs: Envs):
    token = AuthClient(envs).auth(envs.test_username, envs.test_password)
    allure.attach(token, name="token.txt", attachment_type=AttachmentType.TEXT)
    return token


@pytest.fixture
def sign_in(request, users, auth_url, base_url, page: Page, users_from_db):
    with allure.step("Подготовка данных"):
        if not any('aboba' in user.username for user in users_from_db()):
            sign_up(page, base_url, auth_url)
        expected_urls = [f"{base_url}/main", f"{base_url}/profile", f"{base_url}/spending"]
        func_params = signature(request.function).parameters
        if "user_id" in func_params:
            user = users[request.getfixturevalue("user_id")]
        else:
            user = {'login': 'aboba', 'password': '12345'}
    with allure.step("Переход на страницу авторизации"):
        page.goto(f"{auth_url}/login")
        page.wait_for_load_state("networkidle")
    with allure.step("Авторизация"):
        login_page = Login(page)
        login_page.log_in(user['login'], user['password'])
    with allure.step("Проверка успешности авторизации"):
        for _ in range(20):
            current_url = page.url
            if any(url in current_url for url in expected_urls):
                break
            page.wait_for_timeout(500)
        assert page.title() == 'Niffler'
    token = page.evaluate('() => window.localStorage.getItem("id_token")')
    allure.attach(token, name="token", attachment_type=AttachmentType.TEXT)
    return token, {'login': user['login'], 'password': user['password']}
