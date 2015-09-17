# -*- coding: utf-8 -*-
from textminer import filters
from textminer.matchers import RegexMatcher, StringMatcher
from textminer.util import Dict
import doctest
import loggingd

log = loggingd.getLogger(__name__)

class ExtractError(Exception):
    pass

class Extractor(object):
    def __init__(self, rule):
        self._rule = rule
        self._prefix_matcher = None
        self._suffix_matcher = None
        self._filters = None
        self._child = None
        self._compile(rule)
        
    def extract(self, text):
        try:
            return self._extract(text)
        except:
            short_text = text[:100] + ' ...' if len(text) > 100 else text
            msg = 'Failed to extract.\nRule:\n%s\nText:\n%s' % (self._rule, short_text)
            log.warn(msg, exc_info=True)
            raise ExtractError(msg)
        
    def _extract(self, text):
        raise NotImplementedError()
    
    def _compile(self, rule):
        self._prefix_matcher = _compile_pattern(rule['prefix'])
        self._suffix_matcher = _compile_pattern(rule['suffix'])
        self._filters = _compile_filters(rule.get('filters'))
        self._child = _compile_child(rule)
        
    def _filter(self, value):
        '''
        >>> p = Extractor({'prefix': '<html>', 'suffix': '</html>'})
        >>> p._filters = ['default(value, "0")', 'int(value)']
        >>> p._filter(None)
        0
        '''
        for f in self._filters:
            value = eval(f, filters.FILTERS, {'value': value})
        return value
        
    def _process_child(self, value):
        '''
        >>> e = Extractor({'prefix': '<html>', 'suffix': '</html>'})
        >>> e._process_child('<div>aaa</div>')
        '<div>aaa</div>'
        
        >>> e._child = ValueExtractor({'prefix': '<div>', 'suffix': '</div>'})
        >>> e._process_child('<div>aaa</div>')
        'aaa'
        
        >>> e._process_child(None) is None
        True
        '''
        if self._child is None or value is None:
            return value
        return self._child.extract(value)
        
class ValueExtractor(Extractor):
    def _extract(self, text):
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
    def _extract(self, text):
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
        
    def _extract(self, text):
        '''
        >>> p = DictExtractor([{'key': 'name', 'prefix': '<td id="1">', 'suffix': '</td>'}, {'key': 'value', 'prefix': '<td id="2">', 'suffix': '</td>'}])
        
        >>> d = p.extract('<tr><td id="1">abc</td><td id="2">123</td></tr>')
        >>> d['name']
        'abc'
        >>> d['value']
        '123'
        
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

def _compile_filters(filters):
    '''
    >>> _compile_filters(['int'])
    ['int(value)']
    >>> _compile_filters(['default(0)'])
    ['default(value, 0)']
    >>> _compile_filters(None)
    []
    '''
    results = []
    if filters is not None:
        for f in filters:
            if '(' in f:
                f = f.replace('(', '(value, ', 1)
            else:
                f = f + '(value)'
            results.append(f)
    return results

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
    
    single slash
    >>> _compile_pattern('/').match('a/b', 0)
    ('/', 1, 2)
    '''
    if pattern.startswith('//') and pattern.endswith('//'):
        return StringMatcher(pattern[2:-2])
    elif len(pattern) >= 2 and pattern.startswith('/') and pattern.endswith('/'):
        return RegexMatcher(pattern[1:-1])
    else:
        return StringMatcher(pattern)
    
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
    