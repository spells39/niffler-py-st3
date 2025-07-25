import random

import mimesis
import pytest
from dotenv import load_dotenv
import os

from tests.constants import currencies
from tests.helpers import login, categories, add_category
from tests.pages.main import MainStatisticsPage
from tests.pages.new_spending import Spending

load_dotenv()

from tests.pages.profile import Profile
from tests.pages.sign_up import SignUp

from playwright.sync_api import Page, expect
from tests.pages.login import Login


auth_url = os.getenv("AUTH_URL")
base_url = os.getenv("BASE_URL")
person = mimesis.Person()
num = mimesis.Numeric()


class TestLogin:

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_sign_up(self, page: Page, user_id: int, users):
        user = users[user_id]
        page.goto(f"{auth_url}/register")
        page.wait_for_load_state("networkidle")
        reg_page = SignUp(page)
        reg_page.sign_up(user['login'], user['password'])
        page.wait_for_url(f"{base_url}/main")
        page.wait_for_url(f"{auth_url}/login")
        assert page.title() == "Login to Niffler"

    @pytest.mark.parametrize("user_id",  list(range(11)))
    def test_login(self, page: Page, user_id: int, users):
        user = users[user_id]
        page.goto(f"{auth_url}/login")
        page.wait_for_load_state("networkidle")
        login_page = Login(page)
        login_page.log_in(user['login'], user['password'])
        page.wait_for_url(f"{base_url}/main")
        assert page.title() == "Niffler"

    @pytest.mark.parametrize("user_id",  list(range(11)))
    @pytest.mark.dependency(depends=["test_login"])
    def test_logout(self, page: Page, user_id: int, users):
        user = users[user_id]
        login(page, user)

        main_page = MainStatisticsPage(page)
        main_page.logout()
        page.wait_for_load_state("networkidle")
        page.wait_for_url(f"{auth_url}/login")
        assert page.title() == "Login to Niffler"


class TestProfile:

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_update_profile(self, page: Page, user_id: int, users):
        user = users[user_id]
        login(page, user)

        page.goto(f"{base_url}/profile")
        page.wait_for_load_state("networkidle")
        profile_page = Profile(page)
        new_name = person.name()
        profile_page.update_profile(new_name)
        page.reload()
        name = page.locator("#name").input_value()
        assert name == new_name

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_add_category(self, page: Page, user_id: int, users):
        user = users[user_id]
        login(page, user)

        page.goto(f"{base_url}/profile")
        page.wait_for_load_state("networkidle")
        profile_page = Profile(page)
        user_category = mimesis.Text('en').word()
        profile_page.add_category(user_category)
        page.reload()
        expect(page.get_by_text(user_category, exact=True)).to_be_visible()
        users[user_id]['categories'].append(user_category)

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_archive_category(self, page: Page, user_id:int, users):
        user = users[user_id]
        login(page, user)

        category = mimesis.Text('en').word()
        add_category(page, category)

        page.goto(f"{base_url}/profile")
        page.wait_for_load_state("networkidle")
        profile_page = Profile(page)
        profile_page.archive_category()
        expect(page.locator(f'tr:has-text("{category}")')).not_to_be_visible()

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_edit_category(self, page: Page, user_id: int, users):
        user = users[user_id]
        login(page, user)

        category = mimesis.Text('en').word()
        add_category(page, category)

        page.goto(f"{base_url}/profile")
        page.wait_for_load_state("networkidle")
        profile_page = Profile(page)
        category = mimesis.Text('en').word()
        profile_page.edit_category(category)
        assert page.locator("span", has_text=category).is_visible()
        user['categories'].append(category)


class TestSpending:

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_add_spending_exist_category(self, page: Page, user_id: int, users):
        user = users[user_id]
        login(page, user)

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

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_add_spending_new_category(self, page: Page, user_id: int, users):
        user = users[user_id]
        login(page, user)

        page.goto(f"{base_url}/spending")
        page.wait_for_load_state("networkidle")
        spending_page = Spending(page)
        currency = random.choice(currencies)
        amount = str(num.integer_number(1, 110000))
        user_category = mimesis.Text('en').word()
        desc = mimesis.Text('en').word()
        spending_page.add_spending_new_category(amount, currency, user_category, desc)
        users[user_id]['categories'].append(user_category)
        page.goto(f"{base_url}/main")
        page.wait_for_load_state("networkidle")
        expect(page.get_by_role("checkbox", name=user_category, exact=True)).to_be_visible()

    @pytest.mark.parametrize("user_id", list(range(11)))
    def test_delete_spending(self, page: Page, user_id: int, users):
        user = users[user_id]
        login(page, user)

        main_page = MainStatisticsPage(page)
        cat = random.choice(user['categories'])
        #expect(page.get_by_role("checkbox", name=cat, exact=True)).to_be_visible()
        main_page.delete_row(cat)
        expect(page.get_by_role("checkbox", name=cat)).not_to_be_visible()
