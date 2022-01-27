from setuptools import setup

from setuptools import setup, find_packages

setup(
    name='sir_model',
    version='1.0.0',
    install_requires=[
        'pytest'
    ],
    packages=find_packages()
)