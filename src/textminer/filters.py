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

def strip(value, chars=None):
    '''
    >>> strip(' \tabc def\t ')
    'abc def'
    >>> strip('"abc"', '"')
    'abc'
    '''
    return value.strip(chars)

def strip_html(value):
    '''
    >>> strip_html('a<b>b</b>c')
    'abc'
    '''
    value = util.compact_html(value)
    return re.sub('<.+?>', '', value)

def _wrap(func):
    '''
    >>> def func(value): return value + 1
    >>> func = _wrap(func)
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
    'bool': _wrap(bool),
    'date': _wrap(date),
    'datetime': _wrap(datetime),
    'eval': _wrap(eval),
    'float': _wrap(float),
    'int': _wrap(int),
    'strip': _wrap(strip),
    'strip_html': _wrap(strip_html),
}
    
if __name__ == '__main__':
    doctest.testmod()
    