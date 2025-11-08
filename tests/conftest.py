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

from tests.clients.kafka_client import KafkaClient
from tests.models.config import Envs
from tests.utils.UsersData import get_user_data

pytest_plugins = ["tests.fixtures.auth", "tests.fixtures.clients", "tests.fixtures.pages", "tests.fixtures.soap",
                  "tests.grpc.tests"]

person = mimesis.Person()

_CACHED_USERS = None


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


def pytest_collection_modifyitems(items):
    CLASS_ORDER = ["TestKafkaUserData", "TestAPI", "TestDB", "TestSoap", "TestCalculateRate", "TestGetAllCurrencies",
                   "TestWiremockCurrencies", "TestLogin", "TestProfile", "TestSpending"]
    class_mapping = {item: item.cls.__name__ for item in items if hasattr(item, 'cls') and item.cls}

    sorted_items = []

    # Сначала добавляем классы в указанном порядке
    for class_name in CLASS_ORDER:
        class_items = [item for item in items if class_mapping.get(item) == class_name]
        sorted_items.extend(class_items)

    # Потом все остальные классы
    other_items = [item for item in items if class_mapping.get(item) not in CLASS_ORDER]
    sorted_items.extend(other_items)

    items[:] = sorted_items


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
        userdata_db_url=os.getenv("USERDATA_DB_URL"),
        kafka=os.getenv("KAFKA")
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


@pytest.fixture(scope="session")
def kafka(envs):
    with KafkaClient(envs) as k:
        yield k


@pytest.fixture(scope="module")
def user_data(request):
    file_path = str(request.fspath)
    return get_user_data(file_path)


@pytest.fixture(scope="module")
def users(user_data):
    return user_data.get_users()
