import pytest

from app import create_app
from app import db

pytest_plugins = [
    "app.tests.factories",
]


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def app():
    _app = create_app({'TESTING': True})
    ctx = _app.app_context()
    ctx.push()
    yield _app
    ctx.pop()


@pytest.fixture(scope="session")
def _db(app):
    """
    Returns session-wide initialised database.
    """
    db.drop_all()
    db.create_all()
    return db
