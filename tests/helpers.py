import allure
import mimesis
from playwright.sync_api import Page
from dotenv import load_dotenv
from tests.pages.profile import Profile
from tests.pages.sign_up import SignUp

load_dotenv()


def add_category(page: Page, category: str, url: str):
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


def sign_up(page: Page, base_url, auth_url):
    user = {'login': 'aboba', 'password': '12345'}
    page.goto(f"{auth_url}/register")
    page.wait_for_load_state("networkidle")
    reg_page = SignUp(page)
    reg_page.sign_up(user['login'], user['password'])
    page.wait_for_url(f"{base_url}/main")
    page.wait_for_url(f"{auth_url}/login")
    assert page.title() == "Login to Niffler"
