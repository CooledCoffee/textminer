# -*- coding: utf-8 -*-
from datetime import datetime as DateTime
from textminer import util
import doctest
import re
import six

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

def eval(value, expression):
    '''
    >>> eval(10, 'value / 10') == 1
    True
    '''
    if six.PY2:
        import __builtin__ as builtins
    else:
        import builtins
    return builtins.eval(expression, FILTERS, {'value': value})

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

def _none_wrapper(func):
    '''
    >>> def func(value): return value + 1
    >>> func = _none_wrapper(func)
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

def _number_wrapper(func):
    '''
    >>> func = _number_wrapper(int)
    >>> func('1,234,567')
    1234567
    '''
    def wrapper(value, *args):
        value = value.replace(',', '')
        return func(value, *args)
    return wrapper

FILTERS = {
    'default': default,
    'bool': _none_wrapper(bool),
    'date': _none_wrapper(date),
    'datetime': _none_wrapper(datetime),
    'eval': _none_wrapper(eval),
    'float': _none_wrapper(_number_wrapper(float)),
    'int': _none_wrapper(_number_wrapper(int)),
    'strip': _none_wrapper(strip),
    'strip_html': _none_wrapper(strip_html),
}
    
if __name__ == '__main__':
    doctest.testmod()
    