from setuptools import setup

from setuptools import setup, find_packages

setup(
    name='sir_model',
    version='1.0.0',
    packages=find_packages(include=['model', 'model.*']),
    install_requires=[],
)
