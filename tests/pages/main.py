from playwright.sync_api import Page, expect

from tests.pages.parent_page import ParentPage


class MainStatisticsPage(ParentPage):
    def __init__(self, page: Page):
        super().__init__(page)

        self.total_amount = page.locator("h1:has-text('P') >> nth=0")
        self.user_total_amount = page.locator("h1:has-text('P') >> nth=1")

        self.new_spending_button = page.get_by_role("link", name="New spending")
        self.search_input = page.get_by_placeholder("Search")
        self.time_filter = page.get_by_text("All time")
        self.delete_button = page.get_by_role("button", name="Delete")
        self.pagination_next = page.get_by_role("button", name="Next")
        self.pagination_prev = page.get_by_role("button", name="Previous")

        self.delete_dialog = page.get_by_role("dialog")
        self.confirm_delete_button = self.delete_dialog.get_by_role("button", name="Delete", exact=True)
        self.cancel_delete_button = self.delete_dialog.get_by_role("button", name="Cancel")

        self.menu_button = page.get_by_role("button", name="Menu")
        self.sign_out_button = page.get_by_role("menuitem", name="Sign Out")
        self.logout_button = page.get_by_role("button", name="Log out")

        self.spending_rows = page.locator(".spending-row:visible")
        self.empty_state_message = page.get_by_text("There are no spendings")


    def logout(self):
        self.menu_button.click()
        self.sign_out_button.click()
        self.logout_button.click()

    def delete_row(self, category: str):
        row = self.page.locator(f'tr:has-text("{category}")')
        row.click()
        #self.page.get_by_role("checkbox", name=category).check()
        self.delete_button.click()
        self.delete_dialog.wait_for()
        self.confirm_delete_button.click()