import os
from inspect import signature

import mimesis
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright

from tests.clients.spends_client import SpendsHttpClient
from tests.database.auth_db import AuthDb
from tests.database.spend_db import SpendDb
from tests.helpers import sign_up
from tests.models.config import Envs
from tests.pages.login import Login

person = mimesis.Person()

@pytest.fixture(scope="session")
def envs():
    load_dotenv()
    return Envs(
        front_url=os.getenv("BASE_URL"),
        api_url=os.getenv("API_URL"),
        spend_db_url=os.getenv("SPEND_DB_URL"),
        auth_db_url=os.getenv("USER_DB_URL"),
        test_username=os.getenv("TEST_USERNAME"),
        test_password=os.getenv("TEST_PASSWORD")
    )


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


@pytest.fixture
def sign_in(request, users, auth_url, base_url, page: Page, users_from_db):
    if not any('aboba' in user.username for user in users_from_db()):
        sign_up(page, base_url, auth_url)
    expected_urls = [f"{base_url}/main", f"{base_url}/profile", f"{base_url}/spending"]
    #page = request.getfixturevalue("page")
    func_params = signature(request.function).parameters
    if "user_id" in func_params:
        user = users[request.getfixturevalue("user_id")]
    else:
        user = {'login': 'aboba', 'password': '12345'}
    page.goto(f"{auth_url}/login")
    page.wait_for_load_state("networkidle")
    login_page = Login(page)
    login_page.log_in(user['login'], user['password'])
    for _ in range(20):
        current_url = page.url
        if any(url in current_url for url in expected_urls):
            break
        page.wait_for_timeout(500)
    assert page.title() == 'Niffler'
    token = page.evaluate('() => window.localStorage.getItem("id_token")')
    return token, {'login': user['login'], 'password': user['password']}
