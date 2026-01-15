#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Guation"

from setuptools import setup, find_packages
import pathlib

VERSION = None

exec(pathlib.Path(__file__).parent.joinpath("esa_update/version.py").read_text())

setup(
    name='esa_update',
    version=VERSION,
    author="Guation",
    packages=['esa_update'],
    entry_points={
        'console_scripts': [
            'esa_update = esa_update.esa_update:main'
        ]
    },
    include_package_data=True,
    install_requires=[
        "urllib3==2.2.3",
    ],
    project_urls={
        "url": "https://github.com/Guation/ESAUpdate",
    }
)