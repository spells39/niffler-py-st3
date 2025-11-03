import os

import pytest

from tests.utils.sessions import SoapSession


@pytest.fixture(scope="module")
def soap_session():
    session = SoapSession(url=os.getenv("SOAP"))
    return session