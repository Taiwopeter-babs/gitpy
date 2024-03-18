#!/usr/bin/env python3
"""
Entry point of the module
"""
from setuptools import setup

setup(
    name="gitpy",
    version="1.0",
    packages=["gitpy"],
    entry_points={"console_scripts": ["gitpy = gitpy.cli:main"]},
)
