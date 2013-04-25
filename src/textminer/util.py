# -*- coding: utf-8 -*-
import doctest
import re

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
        except KeyError, k:
            raise AttributeError(k)
    
    def __setattr__(self, key, value): 
        self[key] = value
    
    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError(k)
        
def compactHtml(html):
    '''
    >>> compactHtml('<div id="div1">\\n abc def \\n</div>')
    '<div id="div1">abc def</div>'
    '''
    html = re.sub('\\s', ' ', html)
    html = re.sub(' +', ' ', html)
    return html.replace(' <', '<').replace('> ', '>')

if __name__ == '__main__':
    doctest.testmod()
    