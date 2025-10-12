import os

import allure
import mimesis
from allure_commons.types import AttachmentType
from playwright.sync_api import Page
from dotenv import load_dotenv

from tests.pages.login import Login
from tests.pages.profile import Profile
from tests.pages.sign_up import SignUp

load_dotenv()

front_url=os.getenv("BASE_URL")
auth_url=os.getenv("AUTH_URL")

def add_category_front(page: Page, category: str, url: str):
    with allure.step("Переход на страницу профиля"):
        page.goto(f"{url}/profile")
        page.wait_for_load_state("networkidle")
    with allure.step("Добавление категории"):
        profile_page = Profile(page)
        profile_page.add_category(category)


def categories():
    return [mimesis.Text('en').word() for _ in range(2)]


def invalid_users():
    return [(mimesis.Person().username(), mimesis.Person().password()) for _ in range(3)]


def sign_up_front(page: Page, user=None):
    if user is None:
        user = {'login': 'aboba', 'password': '12345'}
    page.goto(f"{auth_url}/register")
    page.wait_for_load_state("networkidle")
    reg_page = SignUp(page)
    reg_page.sign_up(user['login'], user['password'])
    page.wait_for_url(f"{auth_url}/login")
    assert page.title() == "Login to Niffler"


def sign_up(auth_client, envs, user=None):
    if user is None:
        user = {'login': 'aboba', 'password': '12345'}
    resp = auth_client.register(user['login'], user['password'], envs)
    assert resp.status_code == 201
    return resp


def sign_in_front(user, users_from_db, page: Page):
    with allure.step("Подготовка данных"):
        if not any(user['login'].lower() == u.username.lower() for u in users_from_db):
            sign_up_front(page, user)
        expected_urls = [f"{front_url}/main", f"{front_url}/profile", f"{front_url}/spending"]
    with allure.step("Переход на страницу авторизации"):
        page.goto(f"{auth_url}/login")
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


def sign_in(user, users_from_db, auth_client, envs):
    with allure.step("Подготовка данных"):
        if not any(user['login'].lower() == u.username.lower() for u in users_from_db):
            sign_up(auth_client, envs, user)
    with allure.step("Авторизация"):
        resp = auth_client.get_token(user['login'], user['password'], envs)
        return resp
