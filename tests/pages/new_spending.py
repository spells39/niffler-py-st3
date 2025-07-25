from playwright.sync_api import Page, expect
from datetime import datetime

from tests.pages.parent_page import ParentPage


class Spending(ParentPage):
    def __init__(self, page: Page):
        super().__init__(page)

        self.amount_input = page.get_by_role("spinbutton", name="Amount")
        self.currency_select = page.get_by_role("combobox")
        self.category = page.get_by_role("textbox", name="Add new category")
        self.date_input = page.get_by_role("textbox", name="MM/DD/YYYY")
        self.description_input = page.get_by_role("textbox", name="Description")

        self.add_button = page.get_by_role("button", name="Add")
        self.cancel_button = page.get_by_role("button", name="Cancel")

        self.error_messages = page.locator(".error-message")


    def add_spending_new_category(self, amount: str, currency: str, category: str, description: str):
        self.amount_input.fill(amount)
        self.currency_select.click()
        self.page.get_by_role("option", name=currency).click()
        self.category.fill(category)
        self.description_input.fill(description)
        self.add_button.click()

    def add_spending_exist_category(self, amount: str, currency: str, category: str, description: str):
        self.amount_input.fill(amount)
        self.currency_select.click()
        self.page.get_by_role("option", name=currency).click()
        self.page.locator(f'tr:has-text("{category}")').click()
        self.description_input.fill(description)
        self.add_button.click()
