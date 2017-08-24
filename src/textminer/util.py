# -*- coding: utf-8 -*-
import re

import requests

_TIMEOUT = 30

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

def curl(url, charset=None):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/43.0.2357.81 Chrome/43.0.2357.81 Safari/537.36'}
    resp = requests.get(url, headers=headers, timeout=_TIMEOUT)
    resp.raise_for_status()
    if charset is None and resp.headers.get('Content-Type', '').startswith('text/html'):
        charset = _detect_charset(resp.text[:1024])
    if charset is not None:
        resp.encoding = charset
    return compact_html(resp.text)

_CHARSET_PATTERNS = [
    re.compile('<meta http-equiv="content-type" content="text/html; charset=(.*)"'),
    re.compile('<meta charset="(.*)"'),
]
def _detect_charset(head):
    '''
    >>> html = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /></head>'
    >>> _detect_charset(html)
    'utf-8'
    
    >>> html = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>'
    >>> _detect_charset(html)
    'utf-8'
    
    >>> html = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" /></head>'
    >>> _detect_charset(html)
    'utf-8'
    
    >>> html = '<html><head><meta charset="utf-8"></head>'
    >>> _detect_charset(html)
    'utf-8'
    
    >>> html = '<html>'
    >>> _detect_charset(html) is None
    True
    '''
    head = head.lower()
    for pattern in _CHARSET_PATTERNS:
        match = pattern.search(head)
        if match is not None:
            return match.group(1)
