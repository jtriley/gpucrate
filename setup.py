#!/usr/bin/env python
import os
import re

from setuptools import setup, find_packages

version_re = r'^__version__ = ["\']([^"\']*)["\']$'
author_re = r'^__author__ = ["\'](.*)["\']$'

INIT = open(os.path.join('gpucrate', '__init__.py')).read()
version = re.search(version_re, INIT, re.M).group(1)
author = re.search(author_re, INIT, re.M).group(1)

README = open('README.md').read()

setup(
    name='gpucrate',
    version=version,
    packages=find_packages(),
    author=author,
    url="https://github.com/jtriley/gpucrate",
    description=("gpucrate creates hard-linked GPU driver volumes "
                 "for use with docker, singularity, etc."),
    long_description=README,
    install_requires=[
        "sh>=1.11",
        "nvidia-ml-py>=7.352.0",
        "PyYAML>=3.11",
    ],
    setup_requires=[
        'pytest-runner>=2.9'
    ],
    tests_require=[
        "pytest>=3.0.3",
        "pytest-cov>=2.4.0",
        "pytest-flake8>=0.7",
        "testfixtures>=4.10.0",
        "mock>=2.0.0",
    ],
    entry_points=dict(console_scripts=[
        'gpucrate = gpucrate.cli:main',
        'singularity-gpu = gpucrate.cli:singularity_gpu',
    ]),
    include_package_data=True,
    package_data={
        'gpucrate.tests': ['data/*.txt'],
    },
)
