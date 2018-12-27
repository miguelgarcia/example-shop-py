from setuptools import setup

setup(
    entry_points={
        'console_scripts': [
            'app=app.commands:cli',
        ],
    },
)
