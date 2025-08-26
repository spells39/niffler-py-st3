import os
import pytest

from pytest import Item, FixtureRequest
from _pytest.fixtures import FixtureDef

import allure
import mimesis
from allure_commons.reporter import AllureReporter
from allure_commons.types import AttachmentType
from allure_pytest.listener import AllureListener
from dotenv import load_dotenv
from tests.models.config import Envs

pytest_plugins = ["tests.fixtures.auth", "tests.fixtures.clients", "tests.fixtures.pages"]

person = mimesis.Person()


def allure_logger(config) -> AllureReporter:
    listener: AllureListener = config.pluginmanager.get_plugin("allure_listener")
    return listener.allure_logger


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_call(item: Item):
    yield
    allure.dynamic.title(" ".join(item.name.split("_")[1:]).title())


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_fixture_setup(fixturedef: FixtureDef, request: FixtureRequest):
    yield
    logger = allure_logger(request.config)
    item = logger.get_last_item()
    scope_letter = fixturedef.scope[0].upper()
    item.name = f"[{scope_letter}] " + " ".join(fixturedef.argname.split("_")).title()


@pytest.fixture(scope="session")
def envs():
    load_dotenv()
    env_instance =  Envs(
        front_url=os.getenv("BASE_URL"),
        api_url=os.getenv("API_URL"),
        auth_url=os.getenv("AUTH_URL"),
        auth_secret=os.getenv("AUTH_SECRET"),
        spend_db_url=os.getenv("SPEND_DB_URL"),
        auth_db_url=os.getenv("USER_DB_URL"),
        test_username=os.getenv("TEST_USERNAME"),
        test_password=os.getenv("TEST_PASSWORD")
    )
    allure.attach(env_instance.model_dump_json(), name="envs", attachment_type=AttachmentType.JSON)
    return env_instance


@pytest.fixture(scope="session")
def base_url(envs):
    return os.getenv("BASE_URL")


@pytest.fixture(scope="session")
def api_url(envs):
    return os.getenv("API_URL")


@pytest.fixture(scope="session")
def auth_url(envs):
    return os.getenv("AUTH_URL")


@pytest.fixture(scope="session", autouse=True)
def users():
    users = [{'login': 'aboba', 'password': '12345', 'categories': [], 'spendings': []}]
    for i in range(10):
        users.append({
            "login": person.username(),
            "password": person.password(),
            "categories": [],
            "spendings": []
        })
    yield users
