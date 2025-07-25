from playwright.sync_api import Page

from tests.pages.parent_page import ParentPage


class Profile(ParentPage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.upload_picture_button = page.get_by_text("Upload new picture")
        self.username_input = page.get_by_label("Username")
        self.name_input = page.locator("#name")
        self.save_button = page.get_by_role("button", name="Save changes")

        self.add_category_input = page.get_by_role("textbox", name="Add new category")
        self.show_archived_checkbox = page.get_by_label("Show archived")

        self.success_message = page.get_by_text("Profile successfully updated")
        self.success_message_category = page.get_by_text("You've added new category")

        self.menu_button = page.get_by_role("button", name="Menu")
        self.sign_out_button = page.get_by_role("menuitem", name="Sign Out")
        self.logout_button = page.get_by_role("button", name="Log out")

    def update_profile(self, name: str):
        self.name_input.fill(name)
        self.save_button.click()
        self.success_message.wait_for()

    def add_category(self, category_name: str):
        self.add_category_input.fill(category_name)
        self.add_category_input.press("Enter")

    def archive_category(self):
        self.page.get_by_role("button", name="Archive category").first.click()
        self.page.get_by_role("button", name="Archive").click()

    def edit_category(self, category_name: str):
        self.page.get_by_role("button", name="Edit category").first.click()
        self.page.get_by_role("textbox", name="Edit category").click()
        self.page.get_by_role("textbox", name="Edit category").fill(category_name)
        self.page.get_by_role("textbox", name="Edit category").press("Enter")
        self.page.get_by_text("Category name is changed").wait_for()

    def logout(self):
        self.menu_button.click()
        self.sign_out_button.click()
        self.logout_button.click()