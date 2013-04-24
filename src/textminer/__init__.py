# -*- coding: utf-8 -*-
from textminer import extractors, util
import doctest
import importlib
import json
import urllib2
import yaml

def compile(rule, fmt='yaml'):
    '''
    >>> rule = {'value': {'prefix': '<body>', 'suffix': '</body>'}}
    >>> parser = compile(rule, fmt=None)
    >>> type(parser).__name__
    'ValueExtractor'
    '''
    rule = _parse_rule(rule, fmt)
    keys = rule.keys()
    if len(keys) != 1:
        raise Exception('Rule should have one single root element.')
    parser_type = keys[0]
    parser_rule = rule[parser_type]
    return extractors.create(parser_type, parser_rule)
    
def extract(text, rule, fmt='yaml'):
    '''
    >>> extract('<html><body>abc</body></html>', {'value': {'prefix': '<body>', 'suffix': '</body>'}}, fmt=None)
    'abc'
    '''
    extractor = compile(rule, fmt=fmt)
    return extractor.extract(text)

def extract_from_url(url, rule, charset=None, fmt='yaml'):
    html = urllib2.urlopen(url, timeout=30)
    html = util.compactHtml(html)
    return extract(html, rule, fmt=fmt)

def _parse_rule(rule, fmt):
    if fmt is None:
        return rule
    elif fmt == 'yaml':
        return yaml.load(rule)
    elif fmt == 'json':
        return json.loads(rule)
    else:
        raise Exception('Unknown rule format "%s".' % fmt)

if __name__ == '__main__':
    doctest.testmod()
    