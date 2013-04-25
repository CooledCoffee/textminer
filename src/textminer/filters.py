# -*- coding: utf-8 -*-
from textminer import util
import datetime
import doctest
import re

class Filter(object):
    def filter(self, value):
        raise NotImplementedError()
    
class DefaultFilter(Filter):
    def __init__(self, default):
        super(DefaultFilter, self).__init__()
        self._default = default
        
    def filter(self, value):
        '''
        >>> f = DefaultFilter('0')
        >>> f.filter('1')
        '1'
        >>> f.filter(None)
        '0'
        '''
        return self._default if value is None else value
    
class TypeFilter(Filter):
    def __init__(self, type):
        super(TypeFilter, self).__init__()
        self._type = type
        
    def filter(self, value):
        '''
        >>> TypeFilter('int').filter(None) is None
        True
        >>> TypeFilter('string').filter('abc')
        'abc'
        >>> TypeFilter('int').filter('123')
        123
        >>> TypeFilter('int').filter('12,345')
        12345
        >>> TypeFilter('float').filter('1.23')
        1.23
        >>> TypeFilter('float').filter('1,234.56')
        1234.56
        >>> TypeFilter('bool').filter('1')
        True
        >>> TypeFilter('bool').filter('')
        False
        >>> TypeFilter('date:%Y-%m-%d').filter('2011-01-01')
        datetime.date(2011, 1, 1)
        >>> TypeFilter('datetime:%Y-%m-%d %H:%M:%S').filter('2011-01-01 12:30:40')
        datetime.datetime(2011, 1, 1, 12, 30, 40)
        >>> TypeFilter('unknown_type').filter('abc')
        Traceback (most recent call last):
        ...
        Exception: Unknown type "unknown_type".
        '''
        if value is None:
            return None
        if self._type == 'string':
            return value
        elif self._type == 'int':
            return int(value.replace(',', ''))
        elif self._type == 'float':
            return float(value.replace(',', ''))
        elif self._type == 'bool':
            return bool(value)
        elif self._type.startswith('date:'):
            pattern = self._type[len('date:'):]
            return datetime.datetime.strptime(value, pattern).date()
        elif self._type.startswith('datetime:'):
            pattern = self._type[len('datetime:'):]
            return datetime.datetime.strptime(value, pattern)
        else:
            raise Exception('Unknown type "%s".' % self._type)
        
class StripHtmlFilter(Filter):
    def filter(self, value):
        '''
        >>> f = StripHtmlFilter()
        >>> f.filter(None) is None
        True
        >>> f.filter('a<b>b</b>c')
        'abc'
        '''
        if value is None:
            return None
        value = util.compact_html(value)
        return re.sub('<.+?>', '', value)
    
class TransformFilter(Filter):
    def __init__(self, expression):
        super(TransformFilter, self).__init__()
        self._expression = expression
        
    def filter(self, value):
        '''
        >>> TransformFilter('value * 1000').filter(None) is None
        True
        >>> TransformFilter('value * 1000').filter(1)
        1000
        >>> TransformFilter('value.upper()').filter('abc')
        'ABC'
        '''
        if value is None:
            return None
        return eval(self._expression, { 'value' : value })
        
if __name__ == '__main__':
    doctest.testmod()
    