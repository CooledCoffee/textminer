# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='textminer',
    version='1.1.1',
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
    packages=['textminer'],
    install_requires=['requests'],
    url='https://github.com/CooledCoffee/textminer/',
)
