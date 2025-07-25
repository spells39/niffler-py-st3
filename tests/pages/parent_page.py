from playwright.sync_api import Page


class ParentPage:
    def __init__(self, page: Page):
        self.page = page