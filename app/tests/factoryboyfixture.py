import pytest
import sys
import inflection
import factory

def get_factory_name(factory_class):
    """Get factory fixture name by factory."""
    return inflection.underscore(factory_class.__name__)

def make_fixture(cls):
    def _update_session(factory_class, session):
        factory_class._meta.sqlalchemy_session = session
        for attr, value in factory_class._meta.declarations.items():
            if isinstance(value, (factory.SubFactory, factory.RelatedFactory)):
                _update_session(value.get_factory(), session)

    def fix_func(session):
        _update_session(cls, session)
        return cls
    fixture=pytest.fixture(fix_func)
    setattr(sys.modules[cls.__module__], get_factory_name(cls), fixture)
    return cls