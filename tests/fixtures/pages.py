import allure
import pytest
from allure_commons.types import AttachmentType
from playwright.sync_api import Page

from tests.utils.helpers import sign_up_front
from tests.pages.login import Login


@pytest.fixture
def sign_in_front(auth_url, base_url, page: Page, users_from_db, user_data):
    def sign_in_front(user=None):
        with allure.step("Подготовка данных"):
            if user is None:
                user = user_data.get_user(user_id=0)
            if not any(user['login'].lower() == u.username.lower() for u in users_from_db()):
                sign_up_front(page, user)
            expected_urls = [f"{base_url}/main", f"{base_url}/profile", f"{base_url}/spending"]
        with allure.step("Переход на страницу авторизации"):
            page.goto(f"{auth_url}/login")
            # page.wait_for_load_state("networkidle")
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

    return sign_in_front
