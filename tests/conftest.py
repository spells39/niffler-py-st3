from typing import List, Dict

import mimesis
import pytest
from playwright.sync_api import Page, sync_playwright

person = mimesis.Person()

@pytest.fixture(scope="function")
def open_page() -> Page:
    with sync_playwright() as sp:
        browser = sp.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        yield page
        browser.close()


@pytest.fixture(scope="session", autouse=True)
def users():
    users = [{'login': 'aboba', 'password': '12345', 'categories': []}]
    for i in range(10):
        users.append({
            "login": person.username(),
            "password": person.password(),
            "categories": []
        })
    #global_users.extend(users)
    yield users
    #global_users.clear()
