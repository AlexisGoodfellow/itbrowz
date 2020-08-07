import pytest
import requests_mock


@pytest.fixture()
def request_mock():
    with requests_mock.Mocker() as m:
        yield m
