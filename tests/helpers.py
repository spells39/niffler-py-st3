import mimesis
from playwright.sync_api import Page
from dotenv import load_dotenv
from tests.pages.profile import Profile

load_dotenv()


def add_category(page: Page, category: str, url: str):
    page.goto(f"{url}/profile")
    page.wait_for_load_state("networkidle")
    profile_page = Profile(page)
    profile_page.add_category(category)


def categories():
    return [mimesis.Text('en').word() for _ in range(2)]


def invalid_users():
    return [(mimesis.Person().username(), mimesis.Person().password()) for _ in range(3)]
