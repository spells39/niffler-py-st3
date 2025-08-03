import random

import mimesis
import pytest
from dotenv import load_dotenv

from tests.constants import currencies
from tests.helpers import add_category, invalid_users
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

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_sign_up(self, page: Page, user_id: int, users, base_url, auth_url):
        user = users[user_id]
        page.goto(f"{auth_url}/register")
        page.wait_for_load_state("networkidle")
        reg_page = SignUp(page)
        reg_page.sign_up(user['login'], user['password'])
        page.wait_for_url(f"{base_url}/main")
        page.wait_for_url(f"{auth_url}/login")
        assert page.title() == "Login to Niffler"

    def test_invalid_sign_up(self, page: Page, auth_url):
        login = 'ab'
        password = '12345'
        page.goto(f"{auth_url}/register")
        page.wait_for_load_state("networkidle")
        reg_page = SignUp(page)
        reg_page.sign_up(login, password, True)
        assert page.get_by_text("Allowed username length").is_visible()

    def test_fill_unmatched_passwords(self, page: Page, auth_url):
        login = person.username()
        password = person.password()
        second_password = person.password()
        page.goto(f"{auth_url}/register")
        page.wait_for_load_state("networkidle")
        reg_page = SignUp(page)
        reg_page.sign_up(login, password, True, second_password)
        assert page.get_by_text("Passwords should be equal").is_visible()

    def test_sign_up_with_used_parameters(self, page: Page, auth_url, users):
        user = users[0]
        page.goto(f"{auth_url}/register")
        page.wait_for_load_state("networkidle")
        reg_page = SignUp(page)
        reg_page.sign_up(user['login'], user['password'], True)
        assert page.get_by_text(f"Username `{user['login']}` already")

    @pytest.mark.parametrize("user_id",  list(range(11)))
    def test_login(self, page: Page, user_id: int, users, auth_url, base_url):
        user = users[user_id]
        page.goto(f"{auth_url}/login")
        page.wait_for_load_state("networkidle")
        login_page = Login(page)
        login_page.log_in(user['login'], user['password'])
        page.wait_for_url(f"{base_url}/main")
        assert page.title() == "Niffler"

    @pytest.mark.parametrize("user", invalid_users())
    def test_invalid_login(self, page: Page, user, auth_url):
        login, password = user
        page.goto(f"{auth_url}/login")
        page.wait_for_load_state("networkidle")
        login_page = Login(page)
        login_page.log_in(login, password)
        error_div = page.locator("form div")
        expect(error_div).to_have_text("Bad credentials")

    @pytest.mark.parametrize("user_id",  list(range(11)))
    @pytest.mark.dependency(depends=["test_login"])
    def test_logout(self, page: Page, user_id: int, sign_in, auth_url):
        main_page = MainStatisticsPage(page)
        main_page.logout()
        page.wait_for_load_state("networkidle")
        page.wait_for_url(f"{auth_url}/login")
        assert page.title() == "Login to Niffler"


class TestProfile:

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_update_profile(self, page: Page, user_id: int, sign_in, base_url):
        page.goto(f"{base_url}/profile")
        page.wait_for_load_state("networkidle")
        profile_page = Profile(page)
        new_name = person.name()
        profile_page.update_profile(new_name)
        page.reload()
        name = page.locator("#name").input_value()
        assert name == new_name

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_add_category(self, page: Page, user_id: int, users, sign_in, base_url):
        page.goto(f"{base_url}/profile")
        page.wait_for_load_state("networkidle")
        profile_page = Profile(page)
        user_category = mimesis.Text('en').word()
        profile_page.add_category(user_category)
        page.reload()
        expect(page.get_by_role("button", name=user_category)).to_be_visible()
        users[user_id]['categories'].append(user_category)

    def test_add_invalid_category(self, page: Page, users, base_url, auth_url, sign_in):
        page.goto(f"{base_url}/profile")
        page.wait_for_load_state("networkidle")
        profile_page = Profile(page)
        user_category = 'a'
        profile_page.add_category(user_category)
        expect(page.get_by_text("Allowed category length is")).to_be_visible()

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_archive_category(self, page: Page, user_id:int, sign_in, base_url):
        category = mimesis.Text('en').word()
        add_category(page, category, base_url)

        page.goto(f"{base_url}/profile")
        page.wait_for_load_state("networkidle")
        profile_page = Profile(page)
        profile_page.archive_category()
        page.reload()
        expect(page.locator(f'tr:has-text("{category}")')).not_to_be_visible()

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_edit_category(self, page: Page, user_id: int, users, sign_in, base_url):
        category = mimesis.Text('en').word()
        add_category(page, category, base_url)

        page.goto(f"{base_url}/profile")
        page.wait_for_load_state("networkidle")
        profile_page = Profile(page)
        category = mimesis.Text('en').word()
        profile_page.edit_category(category)
        page.reload()
        expect(page.get_by_text(category)).to_be_visible()
        users[user_id]['categories'].append(category)

    def test_invalid_edit_category(self, page: Page, users, base_url, auth_url, sign_in):
        category = mimesis.Text('en').word()
        add_category(page, category, base_url)

        page.goto(f"{base_url}/profile")
        page.wait_for_load_state("networkidle")
        profile_page = Profile(page)
        category = '+'
        profile_page.edit_category(category, True)
        expect(page.get_by_text("Allowed category length is")).to_be_visible()


class TestSpending:

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_add_spending_exist_category(self, page: Page, user_id: int, users, sign_in, base_url):
        user = users[user_id]

        page.goto(f"{base_url}/spending")
        page.wait_for_load_state("networkidle")
        spending_page = Spending(page)
        currency = currencies[random.randint(0, len(currencies) - 1)]
        amount = str(num.integer_number(1, 110000))
        user_category = random.choice(user['categories'])
        desc = mimesis.Text('en').word()
        spending_page.add_spending_exist_category(amount, currency, user_category, desc)
        page.goto(f"{base_url}/main")
        page.wait_for_load_state("networkidle")
        expect(page.get_by_role("checkbox", name=user_category, exact=True)).to_be_visible()
        users[user_id]['spendings'].append(user_category)

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_add_spending_new_category(self, page: Page, user_id: int, users, sign_in, base_url):
        page.goto(f"{base_url}/spending")
        page.wait_for_load_state("networkidle")
        spending_page = Spending(page)
        currency = random.choice(currencies)
        amount = str(num.integer_number(1, 110000))
        user_category = mimesis.Text('en').word()
        desc = mimesis.Text('en').word()
        spending_page.add_spending_new_category(amount, currency, user_category, desc)
        page.goto(f"{base_url}/main")
        page.wait_for_load_state("networkidle")
        expect(page.get_by_role("checkbox", name=user_category, exact=True)).to_be_visible()
        users[user_id]['categories'].append(user_category)
        users[user_id]['spendings'].append(user_category)

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_edit_spending(self, page: Page, auth_url, base_url, sign_in, user_id: int, users):
        user = users[user_id]
        page.goto(f"{base_url}/main")
        page.wait_for_load_state("networkidle")
        spending = random.choice(user['spendings'])
        row = page.locator("tr").filter(has=page.locator(f'span:has-text("{spending}")'))
        row.locator('button[aria-label="Edit spending"]').click()
        page.get_by_role("heading", name="Edit spending").wait_for()
        spending_page = Spending(page)
        spending_edit = mimesis.Text('en').word()
        spending_page.edit_spending(category=spending_edit)
        sp_id = next(_ for _ in range(len(user['spendings'])) if user['spendings'][_] == spending)
        users[user_id]['spendings'][sp_id] = spending_edit

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_search_spending(self, page: Page, sign_in, base_url, user_id: int, users):
        user = users[user_id]
        page.goto(f"{base_url}/main")
        page.wait_for_load_state("networkidle")
        main_page = MainStatisticsPage(page)
        category = random.choice(user['spendings'])
        main_page.search(category)

    def test_invalid_add_spending_new_category(self, page: Page, users, base_url, auth_url, sign_in):
        page.goto(f"{base_url}/spending")
        page.wait_for_load_state("networkidle")
        spending_page = Spending(page)
        currency = random.choice(currencies)
        amount = '-10'
        user_category = 'abcde'
        desc = 'desc'
        spending_page.add_spending_new_category(amount, currency, user_category, desc)
        expect(page.get_by_text("Amount has to be not less then")).to_be_visible()

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_delete_spending(self, page: Page, user_id: int, users, sign_in):
        user = users[user_id]

        main_page = MainStatisticsPage(page)
        cat = random.choice(user['spendings'])
        main_page.delete_row(cat)
        page.reload()
        expect(page.get_by_role("checkbox", name=cat)).not_to_be_visible()
        users[user_id]['spendings'].remove(cat)

    def test_delete_all_spendings(self, page: Page, sign_in):
        main_page = MainStatisticsPage(page)
        main_page.delete_all()
        page.reload()
        checkboxes = page.get_by_role("checkbox")
        assert checkboxes.count() == 0

