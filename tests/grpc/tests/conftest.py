import grpc
import pytest
from grpc import insecure_channel

from tests.grpc.internal.grpc.interceptors.allure import AllureInterceptor
from tests.grpc.internal.grpc.interceptors.logging import LoggingInterceptor
from tests.grpc.internal.pb.niffler_currency_pb2_pbreflect import NifflerCurrencyServiceClient
from tests.grpc.settings.settings import Settings

INTERCEPTORS = [
    LoggingInterceptor(),
    AllureInterceptor()
]

@pytest.fixture(scope='session')
def settings() -> Settings:
    return Settings()

# def pytest_addoption(parser: pytest.Parser) -> None:
#     parser.addoption("--mock", action="store_true", default=False)

@pytest.fixture(scope='session')
def grpc_client(settings: Settings, request: pytest.FixtureRequest) -> NifflerCurrencyServiceClient:
    host = settings.currency_service_host
    if request.config.getoption('--mock'):
        host = settings.wiremock_host
    channel = insecure_channel(host)
    intercepted_channel = grpc.intercept_channel(channel, *INTERCEPTORS)
    return NifflerCurrencyServiceClient(intercepted_channel)