#!/usr/bin/env python
import os

from setuptools import setup, find_packages

VERSION = 0.1
version = os.path.join('nvs', '__init__.py')
execfile(version)

README = open('README.md').read()

setup(
    name='nvidia-singularity',
    version=VERSION,
    packages=find_packages(),
    author='Justin Riley',
    author_email='justin_riley@harvard.edu',
    url="https://github.com/fasrc/nvidia-singularity",
    description="Utilities to build and run NVIDIA Singularity images",
    long_description=README,
    install_requires=[
        "sh>=1.11",
        "nvidia-ml-py>=7.352.0",
    ],
    entry_points=dict(console_scripts=[
        'nvidia-singularity = nvs.cli:main',
    ]),
)
