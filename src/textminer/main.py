# -*- coding: utf-8 -*-
import doctest
import json
import requests
import yaml

HTTP_TIMEOUT = 30

def compile(rule, fmt='yaml'):
    '''
    >>> rule = {'value': {'prefix': '<body>', 'suffix': '</body>'}}
    >>> parser = compile(rule, fmt=None)
    >>> type(parser).__name__
    'ValueExtractor'
    '''
    from textminer import extractors
    rule = _parse_rule(rule, fmt)
    keys = list(rule.keys())
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

def extract_from_url(url, rule, fmt='yaml'):
    from textminer import util
    html = requests.get(url, timeout=HTTP_TIMEOUT).text
    html = util.compact_html(html)
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
    