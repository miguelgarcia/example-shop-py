# example-shop-py

[![CircleCI](https://circleci.com/gh/miguelgarcia/example-shop-py.svg?style=svg)](https://circleci.com/gh/miguelgarcia/example-shop-py)

This is a demo project that implements a REST API for a "pretty simple shop" using:

- Python3
- Flask 1.0
- SQLAlchemy
- Marshmallow 3
- factoryboy
- pytest
- CircleCI
- Flake8

Besides CRUD functionality the API will also exposes statistics, produced with custom SQLAlchemy queries

- Products count by category
- Customers count by country
- Orders count by status
- Products sells
- Units delivered by product by country

# TODO

- Implement statistics API
- OpenAPI YAML Spec
- Model diagram
- Dockerize

# Local development environment

    python3 -m venv venv
    . ./venv/bin/activate
    pip install -r requirements.txt
    export FLASK_APP=project.server
    flask db upgrade
    flask db populate_db

    
## Run

    . ./venv/bin/activate
    export FLASK_APP=project.server
    flask run
    
## Run tests

    . ./venv/bin/activate
    pytest
    
