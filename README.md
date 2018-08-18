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

Besides CRUD functionality the API also exposes statistics, produced with custom SQLAlchemy queries

- Products count by category
- Customers count by country
- Orders count by status
- Products sells
- Units delivered by product by country


Complete REST api documentation can be found in the `openapi.yaml` file. Use 
http://editor.swagger.io to load the yaml file and play with de API (point line 8 of `openapi.yaml` to your server, ex: `url: 'http://localhost:5000/api'`.

- Model diagram

![Model diagram](https://raw.githubusercontent.com/miguelgarcia/example-shop-py/master/dbmodel.png)

# Local development environment

    python3 -m venv venv
    . ./venv/bin/activate
    pip install -r requirements.txt
    pip install -e .
    app db upgrade
    app db populate_db
    
## Run

    . ./venv/bin/activate
    app run
    
## Run tests

    . ./venv/bin/activate
    pytest
    
# Building Docker Image

    docker build . -t example-shop-py

## Running docker

An example docker-compose.yml is provided. It creates two containers, the app
and a PostgreSQL database.

Try it running:

    docker-compose up

App will be published at http://localhost:5000/