from inspect import signature

import allure
import pytest
from allure_commons.types import AttachmentType
from playwright.sync_api import Page, sync_playwright

from tests.utils.helpers import sign_up
from tests.pages.login import Login


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


@pytest.fixture(scope="function")
def open_page() -> Page:
    with sync_playwright() as sp:
        browser = sp.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        yield page
        browser.close()
