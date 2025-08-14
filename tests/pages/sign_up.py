from playwright.sync_api import Page

from tests.pages.login import Login


class SignUp(Login):
    def __init__(self, page: Page):
        super().__init__(page)
        self.login = page.get_by_placeholder("Type your username")
        self.password = page.get_by_placeholder("Type your password")
        self.submit_password = page.get_by_role("textbox", name="Submit password")
        self.button = page.get_by_role("button", name="Sign Up")
        self.link_to_sign_in_button = page.get_by_role("link", name="Sign In")

    def sign_up(self, login: str, password: str, invalid: bool = False, second_password: str = ''):
        self.login.fill(login)
        self.password.fill(password)
        if not second_password:
            self.submit_password.fill(password)
        else:
            self.submit_password.fill(second_password)
        self.button.click()
        if not invalid:
            self.link_to_sign_in_button.wait_for()
            self.link_to_sign_in_button.click()