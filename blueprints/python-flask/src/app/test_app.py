import http
from collections.abc import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from .app import app as flask_app


@pytest.fixture()
def app() -> Iterator[Flask]:
    flask_app.config.update({"TESTING": True})
    yield flask_app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


def test_index(client: FlaskClient) -> None:
    response = client.get('/')
    assert response.status_code == http.HTTPStatus.OK
    assert response.data == """
"""
