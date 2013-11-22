# -*- coding: utf-8 -*-
import doctest
import re
import sys
if sys.version_info.major == 3:
    import builtins  # @UnresolvedImport @UnusedImport
    STRING_TYPE = builtins.str
else:
    import __builtin__
    STRING_TYPE = __builtin__.basestring

class Dict(dict):
    '''
    A Dict object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`.
    
    >>> o = Dict(a=1)
    >>> o.a
    1
    >>> o['a']
    1
    >>> o.a = 2
    >>> o['a']
    2
    >>> del o.a
    >>> o.a
    Traceback (most recent call last):
    ...
    AttributeError: 'a'
    >>> del o.b
    Traceback (most recent call last):
    ...
    AttributeError: 'b'
    '''
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(str(e))
    
    def __setattr__(self, key, value): 
        self[key] = value
    
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as e:
            raise AttributeError(str(e))
        
def compact_html(html):
    '''
    >>> compact_html('<div id="div1">\\n abc def \\n</div>')
    '<div id="div1">abc def</div>'
    '''
    html = re.sub('\\s', ' ', html)
    html = re.sub(' +', ' ', html)
    return html.replace(' <', '<').replace('> ', '>')

def is_python3():
    return sys.version_info.major == 3

def _parse_mime(value):
    '''
    no Content-Type header
    >>> _parse_mime(None)
    (None, None)
    
    text/html
    >>> _parse_mime('text/html; charset=utf-8')
    ('text/html', 'utf-8')
    >>> _parse_mime('text/html;charset=utf-8')
    ('text/html', 'utf-8')
    >>> _parse_mime('text/html; charset=UTF-8')
    ('text/html', 'utf-8')
    
    text/html with no charset
    >>> _parse_mime('text/html')
    ('text/html', None)
    
    non text/html
    >>> _parse_mime('application/json')
    ('application/json', None)
    '''
    if value is None:
        return None, None
    ss = value.split(';')
    ss = [s.strip().lower() for s in ss]
    mime = ss[0]
    charset = ss[1].split('=')[1].lower() if len(ss) > 1 else None
    return mime, charset

def _parse_html_charset(html):
    '''
    >>> html = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /></head></html>'
    >>> _parse_html_charset(html)
    'utf-8'
    
    >>> html = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head></html>'
    >>> _parse_html_charset(html)
    'utf-8'
    
    >>> html = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /></head></html>'
    >>> _parse_html_charset(html)
    'utf-8'
    
    >>> html = '<html></html>'
    >>> _parse_html_charset(html) is None
    True
    '''
    html = html.lower()
    m = re.search('<meta http-equiv="content-type" content="(.+?)"', html)
    if m:
        mime = m.group(1)
        _, charset = _parse_mime(mime)
        return charset
    else:
        return None

if __name__ == '__main__':
    doctest.testmod()
    