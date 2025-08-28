import random

import allure
import mimesis
import pytest
from dotenv import load_dotenv

from tests.utils.constants import currencies
from tests.utils.helpers import add_category, invalid_users
from tests.pages.main import MainStatisticsPage
from tests.pages.new_spending import Spending

load_dotenv()

from tests.pages.profile import Profile
from tests.pages.sign_up import SignUp

from playwright.sync_api import Page, expect
from tests.pages.login import Login


person = mimesis.Person()
num = mimesis.Numeric()


class TestLogin:

    @allure.epic("Аутентификация")
    @allure.feature("Регистрация")
    @allure.story("Регистрация валидного пользователя")
    @pytest.mark.parametrize("user_id", list(range(1,11)))
    def test_sign_up(self, page: Page, user_id: int, users, base_url, auth_url):
        user = users[user_id]
        with allure.step("Переход на страницу регистрации"):
            page.goto(f"{auth_url}/register")
            page.wait_for_load_state("networkidle")
        with allure.step("Регистрация"):
            reg_page = SignUp(page)
            reg_page.sign_up(user['login'], user['password'])
        with allure.step("Проверка успешности регистрации"):
            page.wait_for_url(f"{base_url}/main")
            page.wait_for_url(f"{auth_url}/login")
            assert page.title() == "Login to Niffler"

    @allure.epic("Аутентификация")
    @allure.feature("Регистрация")
    @allure.story("Регистрация невалидного пользователя")
    def test_invalid_sign_up(self, page: Page, auth_url):
        login = 'ab'
        password = '12345'
        with allure.step("Переход на страницу регистрации"):
            page.goto(f"{auth_url}/register")
            page.wait_for_load_state("networkidle")
        with allure.step("Регистрация"):
            reg_page = SignUp(page)
            reg_page.sign_up(login, password, True)
        with allure.step("Проверка получения сообщения об ошибке"):
            assert page.get_by_text("Allowed username length").is_visible()

    @allure.epic("Аутентификация")
    @allure.feature("Регистрация")
    @allure.story("Ввод неверного подтверждения пароля при регистрации")
    def test_fill_unmatched_passwords(self, page: Page, auth_url):
        login = person.username()
        password = person.password()
        second_password = person.password()
        with allure.step("Переход на страницу регистрации"):
            page.goto(f"{auth_url}/register")
            page.wait_for_load_state("networkidle")
        with allure.step("Регистрация"):
            reg_page = SignUp(page)
            reg_page.sign_up(login, password, True, second_password)
        with allure.step("Проверка получения сообщения об ошибке"):
            assert page.get_by_text("Passwords should be equal").is_visible()

    @allure.epic("Аутентификация")
    @allure.feature("Регистрация")
    @allure.story("Использование данных уже существующего пользователя")
    def test_sign_up_with_used_parameters(self, page: Page, auth_url, users):
        user = users[0]
        with allure.step("Переход на страницу регистрации"):
            page.goto(f"{auth_url}/register")
            page.wait_for_load_state("networkidle")
        with allure.step("Регистрация"):
            reg_page = SignUp(page)
            reg_page.sign_up(user['login'], user['password'], True)
        with allure.step("Проверка получения сообщения об ошибке"):
            assert page.get_by_text(f"Username `{user['login']}` already")

    @allure.epic("Аутентификация")
    @allure.feature("Авторизация")
    @allure.story("Вход с валидными данными")
    @pytest.mark.parametrize("user_id",  list(range(11)))
    def test_login(self, page: Page, user_id: int, users, auth_url, base_url):
        user = users[user_id]
        with allure.step("Переход на страницу авторизации"):
            page.goto(f"{auth_url}/login")
            page.wait_for_load_state("networkidle")
        with allure.step("Авторизация"):
            login_page = Login(page)
            login_page.log_in(user['login'], user['password'])
        with allure.step("Проверка успешности авторизации"):
            page.wait_for_url(f"{base_url}/main")
            assert page.title() == "Niffler"

    @allure.epic("Аутентификация")
    @allure.feature("Авторизация")
    @allure.story("Вход с невалидными данными")
    @pytest.mark.parametrize("user", invalid_users())
    def test_invalid_login(self, page: Page, user, auth_url):
        login, password = user
        with allure.step("Переход на страницу авторизации"):
            page.goto(f"{auth_url}/login")
            page.wait_for_load_state("networkidle")
        with allure.step("Авторизация"):
            login_page = Login(page)
            login_page.log_in(login, password)
        with allure.step("Проверка получения сообщения об ошибке"):
            error_div = page.locator("form div")
            expect(error_div).to_have_text("Bad credentials")

    @allure.epic("Аутентификация")
    @allure.feature("Выход")
    @allure.story("Выход")
    @pytest.mark.parametrize("user_id",  list(range(11)))
    @pytest.mark.dependency(depends=["test_login"])
    def test_logout(self, page: Page, user_id: int, sign_in, auth_url):
        main_page = MainStatisticsPage(page)
        with allure.step("Выход"):
            main_page.logout()
        with allure.step("Проверка успешности выхода"):
            page.wait_for_load_state("networkidle")
            page.wait_for_url(f"{auth_url}/login")
            assert page.title() == "Login to Niffler"


class TestProfile:

    @allure.epic("Профиль")
    @allure.feature("Изменение информации о пользователе")
    @allure.story("Изменение имени")
    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_update_profile(self, page: Page, user_id: int, sign_in, base_url):
        with allure.step("Переход на страницу профиля"):
            page.goto(f"{base_url}/profile")
            page.wait_for_load_state("networkidle")
        with allure.step("Редактирование профиля"):
            profile_page = Profile(page)
            new_name = person.name()
            profile_page.update_profile(new_name)
        with allure.step("Проверка"):
            page.reload()
            name = page.locator("#name").input_value()
            assert name == new_name

    @allure.epic("Профиль")
    @allure.feature("Категории")
    @allure.story("Добавление валидной категории")
    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_add_category(self, page: Page, user_id: int, users, sign_in, base_url):
        with allure.step("Переход на страницу профиля"):
            page.goto(f"{base_url}/profile")
            page.wait_for_load_state("networkidle")
        with allure.step("Добавление категории"):
            profile_page = Profile(page)
            user_category = mimesis.Text('en').word()
            profile_page.add_category(user_category)
        with allure.step("Проверка добавления категории"):
            page.reload()
            expect(page.get_by_role("button", name=user_category)).to_be_visible()
            users[user_id]['categories'].append(user_category)

    @allure.epic("Профиль")
    @allure.feature("Категории")
    @allure.story("Добавление невалидной категории")
    def test_add_invalid_category(self, page: Page, users, base_url, auth_url, sign_in):
        with allure.step("Переход на страницу профиля"):
            page.goto(f"{base_url}/profile")
            page.wait_for_load_state("networkidle")
        with allure.step("Добавление категории"):
            profile_page = Profile(page)
            user_category = 'a'
            profile_page.add_category(user_category)
        with allure.step("Проверка получения сообщения об ошибке"):
            expect(page.get_by_text("Allowed category length is")).to_be_visible()

    @allure.epic("Профиль")
    @allure.feature("Категории")
    @allure.story("Архивирование категории")
    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_archive_category(self, page: Page, user_id:int, sign_in, base_url):
        category = mimesis.Text('en').word()
        add_category(page, category, base_url)

        with allure.step("Переход на страницу профиля"):
            page.goto(f"{base_url}/profile")
            page.wait_for_load_state("networkidle")
        with allure.step("Архивирование категории"):
            profile_page = Profile(page)
            profile_page.archive_category()
        with allure.step("Проверка отображения категории"):
            page.reload()
            expect(page.locator(f'tr:has-text("{category}")')).not_to_be_visible()

    @allure.epic("Профиль")
    @allure.feature("Категории")
    @allure.story("Валидное редактирование категории")
    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_edit_category(self, page: Page, user_id: int, users, sign_in, base_url):
        category = mimesis.Text('en').word()
        add_category(page, category, base_url)

        with allure.step("Переход на страницу профиля"):
            page.goto(f"{base_url}/profile")
            page.wait_for_load_state("networkidle")
        with allure.step("Редактирование категории"):
            profile_page = Profile(page)
            category = mimesis.Text('en').word()
            profile_page.edit_category(category)
        with allure.step("Проверка"):
            page.reload()
            expect(page.get_by_text(category)).to_be_visible()
            users[user_id]['categories'].append(category)

    @allure.epic("Профиль")
    @allure.feature("Категории")
    @allure.story("Невалидное редактирование категории")
    def test_invalid_edit_category(self, page: Page, users, base_url, auth_url, sign_in):
        category = mimesis.Text('en').word()
        add_category(page, category, base_url)

        with allure.step("Переход на страницу профиля"):
            page.goto(f"{base_url}/profile")
            page.wait_for_load_state("networkidle")
        with allure.step("Редактирование категории"):
            profile_page = Profile(page)
            category = '+'
            profile_page.edit_category(category, True)
        with allure.step("Проверка получения сообщения об ошибке"):
            expect(page.get_by_text("Allowed category length is")).to_be_visible()


class TestSpending:

    @allure.epic("Главная страница")
    @allure.feature("Траты")
    @allure.story("Добавление траты с существующей категорией")
    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_add_spending_exist_category(self, page: Page, user_id: int, users, sign_in, base_url):
        user = users[user_id]

        with allure.step("Переход на страницу добавления трат"):
            page.goto(f"{base_url}/spending")
            page.wait_for_load_state("networkidle")
        with allure.step("Добавление траты"):
            spending_page = Spending(page)
            currency = currencies[random.randint(0, len(currencies) - 1)]
            amount = str(num.integer_number(1, 110000))
            user_category = random.choice(user['categories'])
            desc = mimesis.Text('en').word()
            spending_page.add_spending_exist_category(amount, currency, user_category, desc)
        with allure.step("Проверка добавления траты"):
            page.goto(f"{base_url}/main")
            page.wait_for_load_state("networkidle")
            expect(page.get_by_role("checkbox", name=user_category, exact=True)).to_be_visible()
            users[user_id]['spendings'].append(user_category)

    @allure.epic("Главная страница")
    @allure.feature("Траты")
    @allure.story("Добавление траты с новой категорией")
    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_add_spending_new_category(self, page: Page, user_id: int, users, sign_in, base_url):
        with allure.step("Переход на страницу добавления трат"):
            page.goto(f"{base_url}/spending")
            page.wait_for_load_state("networkidle")
        with allure.step("Добавление траты"):
            spending_page = Spending(page)
            currency = random.choice(currencies)
            amount = str(num.integer_number(1, 110000))
            user_category = mimesis.Text('en').word()
            desc = mimesis.Text('en').word()
            spending_page.add_spending_new_category(amount, currency, user_category, desc)
        with allure.step("Проверка добавления траты"):
            page.goto(f"{base_url}/main")
            page.wait_for_load_state("networkidle")
            expect(page.get_by_role("checkbox", name=user_category, exact=True)).to_be_visible()
            users[user_id]['categories'].append(user_category)
            users[user_id]['spendings'].append(user_category)

    @allure.epic("Главная страница")
    @allure.feature("Траты")
    @allure.story("Редактирование траты")
    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_edit_spending(self, page: Page, auth_url, base_url, sign_in, user_id: int, users):
        user = users[user_id]
        with allure.step("Переход на главную страницу"):
            page.goto(f"{base_url}/main")
            page.wait_for_load_state("networkidle")
        with allure.step("Редактирование траты"):
            spending = random.choice(user['spendings'])
            row = page.locator("tr").filter(has=page.locator(f'span:has-text("{spending}")'))
            row.locator('button[aria-label="Edit spending"]').click()
            page.get_by_role("heading", name="Edit spending").wait_for()
            spending_page = Spending(page)
            spending_edit = mimesis.Text('en').word()
            spending_page.edit_spending(category=spending_edit)
        with allure.step("Проверка"):
            sp_id = next(_ for _ in range(len(user['spendings'])) if user['spendings'][_] == spending)
            users[user_id]['spendings'][sp_id] = spending_edit

    @allure.epic("Главная страница")
    @allure.feature("Траты")
    @allure.story("Посик траты")
    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_search_spending(self, page: Page, sign_in, base_url, user_id: int, users):
        user = users[user_id]
        with allure.step("Переход на главную страницу"):
            page.goto(f"{base_url}/main")
            page.wait_for_load_state("networkidle")
        with allure.step("Поиск траты"):
            main_page = MainStatisticsPage(page)
            category = random.choice(user['spendings'])
            main_page.search(category)

    @allure.epic("Главная страница")
    @allure.feature("Траты")
    @allure.story("Добавление навалидной траты с новой категорией")
    def test_invalid_add_spending_new_category(self, page: Page, users, base_url, auth_url, sign_in):
        with allure.step("Переход на страницу добавления трат"):
            page.goto(f"{base_url}/spending")
            page.wait_for_load_state("networkidle")
        with allure.step("Добавление траты"):
            spending_page = Spending(page)
            currency = random.choice(currencies)
            amount = '-10'
            user_category = 'abcde'
            desc = 'desc'
            spending_page.add_spending_new_category(amount, currency, user_category, desc)
        with allure.step("Проверка получения сообщения об ошибке"):
            expect(page.get_by_text("Amount has to be not less then")).to_be_visible()

    @allure.epic("Главная страница")
    @allure.feature("Траты")
    @allure.story("Удаление траты")
    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_delete_spending(self, page: Page, user_id: int, users, sign_in):
        user = users[user_id]

        with allure.step("Переход на главную страницу"):
            main_page = MainStatisticsPage(page)
        with allure.step("Удаление траты"):
            cat = random.choice(user['spendings'])
            main_page.delete_row(cat)
        with allure.step("Проверка удаления траты"):
            page.reload()
            expect(page.get_by_role("checkbox", name=cat)).not_to_be_visible()
            users[user_id]['spendings'].remove(cat)

    @allure.epic("Главная страница")
    @allure.feature("Траты")
    @allure.story("Удаление всех трат")
    def test_delete_all_spendings(self, page: Page, sign_in):
        with allure.step("Переход на главную страницу"):
            main_page = MainStatisticsPage(page)
        with allure.step("Удаление всех трат"):
            main_page.delete_all()
        with allure.step("Проверка удаления трат"):
            page.reload()
            checkboxes = page.get_by_role("checkbox")
            assert checkboxes.count() == 0

