# -*- coding: utf-8 -*-
import doctest
import re

class Matcher(object):
    def match(self, text, start):
        raise NotImplementedError()
    
class StringMatcher(Matcher):
    def __init__(self, pattern):
        super(StringMatcher, self).__init__()
        self._pattern = pattern
        
    def match(self, text, start):
        '''
        >>> m = StringMatcher('1')
        >>> m.match('a1a1a', 0)
        ('1', 1, 2)
        >>> m.match('a1a1a', 2)
        ('1', 3, 4)
        >>> m.match('a2a', 0)
        (None, -1, -1)
        '''
        index = text.find(self._pattern, start)
        if index != -1:
            return self._pattern, index, index + len(self._pattern)
        else:
            return None, -1, -1
        
class RegexMatcher(Matcher):
    def __init__(self, pattern):
        super(RegexMatcher, self).__init__()
        self._pattern = re.compile(pattern)
        
    def match(self, text, start):
        '''
        >>> m = RegexMatcher('\\d')
        >>> m.match('a1a1a', 0)
        ('1', 1, 2)
        >>> m.match('a1a1a', 2)
        ('1', 3, 4)
        >>> m.match('aba', 0)
        (None, -1, -1)
        '''
        match = self._pattern.search(text[start:])
        if match:
            return match.group(), start + match.start(), start + match.end()
        else:
            return None, -1, -1
    
if __name__ == '__main__':
    doctest.testmod()
    