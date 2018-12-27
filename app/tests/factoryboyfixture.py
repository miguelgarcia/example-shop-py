import pytest
import sys
import inflection
import factory


def get_factory_name(factory_class):
    """Get factory fixture name by factory."""
    return inflection.underscore(factory_class.__name__)


def _update_session(factory_class, session):
    factory_class._meta.sqlalchemy_session = session
    for attr, value in factory_class._meta.declarations.items():
        if isinstance(value, (factory.SubFactory, factory.RelatedFactory)):
            _update_session(value.get_factory(), session)
    for used_factory in factory_class._used_factories:
        _update_session(used_factory, session)


def make_fixture(uses=[]):
    def decorator(cls):
        def fix_func(db_session):
            _update_session(cls, db_session)
            return cls
        fixture = pytest.fixture(fix_func)
        setattr(sys.modules[cls.__module__], get_factory_name(cls), fixture)
        setattr(cls, '_used_factories', uses)
        return cls
    return decorator
