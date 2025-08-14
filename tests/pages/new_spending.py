from playwright.sync_api import Page

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
        self.save_changes_button = page.get_by_role("button", name="Save changes")

        self.error_messages = page.locator(".error-message")
        self.edit_msg = page.get_by_text("Spending is edited")


    def add_spending_new_category(self, amount: str, currency: str, category: str, description: str):
        self.amount_input.fill(amount)
        self.currency_select.click()
        self.page.get_by_role("option", name=currency).click()
        self.category.click()
        self.category.fill(category)
        self.description_input.fill(description)
        self.add_button.click()

    def add_spending_exist_category(self, amount: str, currency: str, category: str, description: str):
        self.amount_input.click()
        self.amount_input.fill(amount)
        self.currency_select.click()
        self.page.get_by_role("option", name=currency).click()
        self.page.get_by_role("button", name=category).click()
        self.description_input.fill(description)
        self.add_button.click()

    def edit_spending(self, amount: str = None, currency: str = None, category: str = None, description: str = None):
        if amount:
            self.amount_input.click()
            self.amount_input.fill(amount)
        if currency:
            self.currency_select.click()
            self.page.get_by_role("option", name=currency).click()
        if category:
            self.category.click()
            self.category.fill(category)
        if description:
            self.description_input.click()
            self.description_input.fill(description)
        self.save_changes_button.click()
        self.edit_msg.wait_for()
        self.page.locator(f'tr:has(span:has-text("{category}"))').wait_for()

