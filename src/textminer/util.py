# -*- coding: utf-8 -*-
import doctest
import re

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
    