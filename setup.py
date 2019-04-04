# coding: utf-8
import sys
from setuptools import setup, find_packages


def README():
    with open('README.rst') as f:
        return f.read()


setup(
    name='backports.os',
    description="Backport of new features in Python's os module",
    long_description=README(),
    url='https://github.com/pjdelport/backports.os',

    author='Pi Delport',
    author_email='pjdelport@gmail.com',

    package_dir={'': 'src'},
    packages=find_packages('src'),

    setup_requires=['setuptools_scm'],
    use_scm_version=True,

    install_requires=[
        'future;python_version<"3.0"',  # For backport of surrogateescape
    ],

    license='Python Software Foundation License',
    classifiers=[
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
