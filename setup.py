from setuptools import setup

setup(
    entry_points={
        'console_scripts': [
            'app=project.commands:cli',
        ],
    },
)
