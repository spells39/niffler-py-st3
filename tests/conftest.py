import os
from inspect import signature

import mimesis
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright

from tests.pages.login import Login

person = mimesis.Person()

@pytest.fixture(scope="session")
def envs():
    load_dotenv()


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
def sign_in(request, users, auth_url, base_url):
    expected_urls = [f"{base_url}/main", f"{base_url}/profile", f"{base_url}/spending"]
    page = request.getfixturevalue("page")
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
