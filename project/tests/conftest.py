import os
import pytest

from project.server import app as _app
from project.settings import db
from .factories import *

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(scope='session')
def app():
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
