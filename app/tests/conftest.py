import os
import pytest

from alembic.command import upgrade
from alembic.config import Config

from app.factory import create_app
from app.database import db as _db
from .factories import *

TESTDB = 'simple-shop_test.db'
TESTDB_PATH = "/tmp/{}".format(TESTDB)

ALEMBIC_CONFIG = 'migrations/alembic.ini'

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture(scope='session')
def app(request):
    """Session-wide test `Flask` application."""
    app = create_app('app.config.TestingConfig')

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()



def apply_migrations():
    """Applies all alembic migrations."""
    config = Config(ALEMBIC_CONFIG)
    upgrade(config, 'head')


@pytest.fixture(scope='session')
def db(app, request):
    """Session-wide test database."""
    if os.path.exists(TESTDB_PATH):
        os.unlink(TESTDB_PATH)


    _db.app = app
    _db.create_all()
    #apply_migrations()

    yield _db
    _db.drop_all()
    os.unlink(TESTDB_PATH)



@pytest.fixture(scope='function')
def session(db, request):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)
    
    db.session = session
    yield session
    transaction.rollback()
    connection.close()
    session.remove()
