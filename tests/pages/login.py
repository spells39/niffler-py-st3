from playwright.sync_api import Page

from tests.pages.parent_page import ParentPage


class Login(ParentPage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.login = page.get_by_placeholder("Type your username")
        self.password = page.get_by_placeholder("Type your password")
        self.button = page.get_by_role("button", name="Log in")

    def log_in(self, login: str, password: str):
        self.login.fill(login)
        self.password.fill(password)
        self.button.click()
