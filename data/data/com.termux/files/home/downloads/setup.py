
from setuptools import setup, find_packages

setup(
    name="karlfine",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "rich",
        "prompt_toolkit"
    ],
    entry_points={
        'console_scripts':[
            'karlfine=karlfine.cli:main'
        ]
    }
)
