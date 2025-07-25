from typing import Dict

import mimesis
from playwright.sync_api import Page, expect
from dotenv import load_dotenv
import os

from tests.pages.profile import Profile

load_dotenv()

from tests.pages.login import Login


auth_url = os.getenv("AUTH_URL")
base_url = os.getenv("BASE_URL")

def login(page: Page, user: Dict[str, str]):
    page.goto(f"{auth_url}/login")
    page.wait_for_load_state("networkidle")
    login_page = Login(page)
    login_page.log_in(user['login'], user['password'])
    page.wait_for_url(f"{base_url}/main")
    assert page.title() == 'Niffler'


def add_category(page: Page, category: str):
    page.goto(f"{base_url}/profile")
    page.wait_for_load_state("networkidle")
    profile_page = Profile(page)
    profile_page.add_category(category)
    #expect(page.get_by_text(category, exact=True)).to_be_visible()


def categories():
    return [mimesis.Text('en').word() for _ in range(2)]