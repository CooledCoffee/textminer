# -*- coding: utf-8 -*-
from textminer import util
from datetime import datetime as DateTime
import doctest
import re

def default(value, default_value):
    '''
    >>> default(1, 0)
    1
    >>> default(None, 0)
    0
    '''
    return default_value if value is None else value

def date(value, format='%Y-%m-%d'):
    '''
    >>> date('2000-01-01')
    datetime.date(2000, 1, 1)
    '''
    return DateTime.strptime(value, format).date()

def datetime(value, format='%Y-%m-%d %H:%M:%S'):
    '''
    >>> datetime('2000-01-01 12:30:40')
    datetime.datetime(2000, 1, 1, 12, 30, 40)
    '''
    return DateTime.strptime(value, format)

def strip_html(value):
    '''
    >>> strip_html('a<b>b</b>c')
    'abc'
    '''
    value = util.compact_html(value)
    return re.sub('<.+?>', '', value)

def wrap(func):
    '''
    >>> def func(value): return value + 1
    >>> func = wrap(func)
    >>> func(1)
    2
    >>> func(None) is None
    True
    '''
    def wrapper(value, *args):
        if value is None:
            return None
        else:
            return func(value, *args)
    return wrapper

FILTERS = {
    'default': default,
    'bool': wrap(bool),
    'date': wrap(date),
    'datetime': wrap(datetime),
    'eval': wrap(eval),
    'float': wrap(float),
    'int': wrap(int),
    'strip_html': wrap(strip_html),
}
    
if __name__ == '__main__':
    doctest.testmod()
    