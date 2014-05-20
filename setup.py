#!/usr/bin/env python

import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('pypay/__init__.py', 'rU') as pkg_file:
    version = re.search(r'__version__ = \'([0-9\.]+)\'\n', pkg_file.read()).group(1)

with open('README.rst', 'rU') as readme_file:
    readme = readme_file.read()

setup(
    name='pypay',
    version=version,
    description='Confirm Paypal payments via PDT and IPN',
    long_description=readme,
    author='Judd Garratt',
    author_email='judd.garratt@gmail.com',
    url='http://bitbucket.org/juddgarratt/pypay',
    packages=['pypay'],
    package_data={'': ['LICENSE']},
    package_dir={'pypay': 'pypay'},
    include_package_data=True,
    install_requires=['requests', 'six'],
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
