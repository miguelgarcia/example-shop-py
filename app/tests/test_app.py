from app import create_app


def test_config():
    # assert not create_app().testing disabled because CircleCI uses a config
    # with TESTING=True
    assert create_app({'TESTING': True}).testing
