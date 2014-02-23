# -*- coding: utf-8 -*-
from textminer import util
from textminer.filters import DefaultFilter, TypeFilter
from textminer.matchers import RegexMatcher, StringMatcher
from textminer.util import Dict
import doctest
import importlib

class Extractor(object):
    def __init__(self, rule):
        self._prefix_matcher = None
        self._suffix_matcher = None
        self._filters = None
        self._child = None
        self._compile(rule)
        
    def extract(self, text):
        raise NotImplementedError()
    
    def _compile(self, rule):
        self._prefix_matcher = _compile_pattern(rule['prefix'])
        self._suffix_matcher = _compile_pattern(rule['suffix'])
        self._filters = _compile_filters(rule)
        self._child = _compile_child(rule)
        
    def _filter(self, value):
        '''
        >>> p = Extractor({'prefix': '<html>', 'suffix': '</html>'})
        >>> p._filters = [DefaultFilter('0'), TypeFilter('int')]
        >>> p._filter(None)
        0
        '''
        for f in self._filters:
            value = f.filter(value)
        return value
        
    def _process_child(self, value):
        return self._child.extract(value) if self._child else value
        
class ValueExtractor(Extractor):
    def extract(self, text):
        value, _ = self.parse_with_end(text)
        return value
    
    def parse_with_end(self, text):
        '''
        >>> p = ValueExtractor({'prefix': '<body>', 'suffix': '</body>'})
        >>> p.parse_with_end('<html><body>abc</body></html>')
        ('abc', 22)
        >>> p.parse_with_end('<html><header>abc</header></html>')
        (None, 0)
        '''
        value, end = _search(self._prefix_matcher, self._suffix_matcher, text)
        value = self._filter(value)
        value = self._process_child(value)
        return value, end
    
class ListExtractor(Extractor):
    def extract(self, text):
        '''
        >>> p = ListExtractor({'prefix': '<li>', 'suffix': '</li>'})
        >>> p.extract('<ul><li>item1</li><li>item2</li></ul>')
        ['item1', 'item2']
        >>> p.extract('<ul></ul>')
        []
        '''
        items = []
        end = 0
        while True:
            value, end = _search(self._prefix_matcher, self._suffix_matcher, text, end)
            if value is None:
                break
            value = self._filter(value)
            value = self._process_child(value)
            items.append(value)
        return items
    
class DictExtractor(Extractor):
    def __init__(self, *args, **kw):
        self._keys = None
        self._children = None
        super(DictExtractor, self).__init__(*args, **kw)
        
    def _compile(self, rule):
        self._keys = [field['key'] for field in rule]
        self._children = [create('value', field) for field in rule]
        
    def extract(self, text):
        '''
        >>> p = DictExtractor([{'key': 'name', 'type': 'string', 'prefix': '<td id="1">', 'suffix': '</td>'}, {'key': 'value', 'type': 'int', 'prefix': '<td id="2">', 'suffix': '</td>'}])
        
        >>> d = p.extract('<tr><td id="1">abc</td><td id="2">123</td></tr>')
        >>> d['name']
        'abc'
        >>> d['value']
        123
        
        >>> d = p.extract('<tr></tr>')
        >>> d['name'] is None
        True
        >>> d['value'] is None
        True
        '''
        values = Dict()
        end = 0
        for i in range(len(self._keys)):
            values[self._keys[i]], temp_end = self._children[i].parse_with_end(text[end:])
            end += temp_end
        return values
    
def create(parser_type, rule):
    '''
    >>> rule = {'prefix': '<body>', 'suffix': '</body>'}
    >>> parser = create('value', rule)
    >>> type(parser).__name__
    'ValueExtractor'
    '''
    parser_class = globals().get(parser_type.capitalize() + 'Extractor')
    if parser_class is None:
        raise Exception('Extractor with type="%s" could not be found.' % parser_type)
    return parser_class(rule)

def _compile_child(rule):
    '''
    >>> rule = {'prefix': '<body>', 'suffix': '</body>'}
    >>> _compile_child(rule) is None
    True
    
    >>> rule = {'prefix': '<body>', 'suffix': '</body>', 'value': {'prefix': '<b>', 'suffix': '</b>'}}
    >>> child = _compile_child(rule)
    >>> type(child).__name__
    'ValueExtractor'
    '''
    for parser_type in ['value', 'list', 'dict']:
        if parser_type in rule:
            return create(parser_type, rule[parser_type])
    else:
        return None

def _compile_filter(filter):
    '''
    no arg
    >>> filter = _compile_filter('stripHtml')
    >>> type(filter).__name__
    'StripHtmlFilter'
    
    list args
    >>> filter = _compile_filter({'type': ['int']})
    >>> type(filter).__name__
    'TypeFilter'
    
    dict args
    >>> filter = _compile_filter({'type': {'type': 'int'}})
    >>> type(filter).__name__
    'TypeFilter'
    '''
    if isinstance(filter, util.STRING_TYPE) or isinstance(filter, util.STRING_TYPE):
        type = filter
        args = None
    elif isinstance(filter, dict):
        type = list(filter.keys())[0]
        args = filter[type]
    else:
        raise Exception('Bad filter %s.' % filter)
    return _create_filter(type, args)

def _compile_filters(rule):
    '''
    >>> rule = {'default': '0', 'filters': [{'type': ['int']}]}
    >>> filters = _compile_filters(rule)
    >>> [type(f).__name__ for f in filters]
    ['DefaultFilter', 'TypeFilter']
    '''
    filters = []
    if 'default' in rule:
        filters.append(DefaultFilter(rule['default']))
    if 'type' in rule:
        filters.append(TypeFilter(rule['type']))
    if 'filters' in rule:
        for filter in rule['filters']:
            if isinstance(filter, util.STRING_TYPE):
                type = filter
                args = None
            elif isinstance(filter, dict):
                type = list(filter.keys())[0]
                args = filter[type]
            filters.append(_create_filter(type, args))
    return filters

def _compile_pattern(pattern):
    '''
    normal text
    >>> _compile_pattern('a|b').match('a|b', 0)
    ('a|b', 0, 3)
    >>> _compile_pattern('//a|b//').match('/a|b/', 0)
    ('a|b', 1, 4)
    
    regular expression
    >>> _compile_pattern('/a|b/').match('b', 0)
    ('b', 0, 1)
    '''
    if pattern.startswith('//') and pattern.endswith('//'):
        return StringMatcher(pattern[2:-2])
    elif pattern.startswith('/') and pattern.endswith('/'):
        return RegexMatcher(pattern[1:-1])
    else:
        return StringMatcher(pattern)

def _create_filter(name, args):
    '''
    no arg
    >>> filter = _create_filter('stripHtml', None)
    >>> type(filter).__name__
    'StripHtmlFilter'
    
    list args
    >>> filter = _create_filter('type', ['int'])
    >>> type(filter).__name__
    'TypeFilter'
    >>> filter._type
    'int'
    
    dict args
    >>> filter = _create_filter('type', {'type': 'int'})
    >>> type(filter).__name__
    'TypeFilter'
    >>> filter._type
    'int'
    '''
    if args is None:
        args = []
    mod = importlib.import_module('textminer.filters')
    class_name = name[0].upper() + name[1:] + 'Filter'
    filter_class = getattr(mod, class_name)
    if isinstance(args, list):
        return filter_class(*args)
    elif isinstance(args, dict):
        return filter_class(**args)
    else:
        raise Exception('Bad filter args %s.' % args)
    
def _search(prefix_matcher, suffix_matcher, text, start_index=0):
    '''
    >>> prefix_matcher = StringMatcher('<b>')
    >>> suffix_matcher = StringMatcher('</b>')
    
    prefix & suffix found
    >>> _search(prefix_matcher, suffix_matcher, '<div><b>abc</b></div>', 1)
    ('abc', 15)
    
    prefix not found
    >>> _search(prefix_matcher, suffix_matcher, '<div><span>abc</span></div>', 1)
    (None, 1)
    
    prefix found but suffix not found
    >>> _search(prefix_matcher, suffix_matcher, '<div><b>abc</span></div>', 1)
    (None, 1)
    
    prefix is start and suffix is end
    >>> _search(RegexMatcher('^'), RegexMatcher('$'), 'abc')
    ('abc', 3)
    '''
    # find prefix
    matched, _, match_end = prefix_matcher.match(text, start_index)
    if matched is None:
        return (None, start_index)
    start = match_end
    
    # find suffix
    matched, match_start, match_end = suffix_matcher.match(text, start)
    if matched is None:
        return (None, start_index)
    end = match_end
    
    # extract text
    return text[start:match_start], end

if __name__ == '__main__':
    doctest.testmod()
    