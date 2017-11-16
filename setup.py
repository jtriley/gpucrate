#!/usr/bin/env python
from setuptools import setup, find_packages

VERSION = 0.1
README = open('README.md').read()

setup(
    name='gpucrate',
    version=VERSION,
    packages=find_packages(),
    author='Justin Riley',
    author_email='justin_riley@harvard.edu',
    url="https://github.com/fasrc/gpucrate",
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
