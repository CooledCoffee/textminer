# -*- coding: utf-8 -*-
from distutils.core import setup
import setuptools

setup(
    name='textminer',
    version='1.3',
    author='Mengchen LEE',
    author_email='CooledCoffee@gmail.com',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
    description='Extracts content from html using rules.',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    install_requires=[
        'loggingd',
        'requests',
        'six',
    ],
    url='https://github.com/cooledcoffee/textminer'
)
