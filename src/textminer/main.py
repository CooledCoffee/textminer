# -*- coding: utf-8 -*-
from loggingd import log_enter
from textminer import util
import doctest
import json
import re
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

@log_enter('[DEBUG] Crawling {url} ...')
def extract_from_url(url, rule, fmt='yaml'):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/43.0.2357.81 Chrome/43.0.2357.81 Safari/537.36'}
    resp = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
    resp.raise_for_status()
    html = _decode_resp(resp)
    html = util.compact_html(html)
    return extract(html, rule, fmt=fmt)

CHARSET_PATTERNS = [
    re.compile('<meta http-equiv="Content-Type" content="text/html; charset=(.*)"', re.IGNORECASE),
    re.compile('<meta charset="(.*)"', re.IGNORECASE),
]    
def _decode_resp(resp):
    for pattern in CHARSET_PATTERNS:
        match = pattern.search(resp.text[:1000])
        if match is not None:
            charset = match.group(1)
            resp.encoding = charset
            break
    return resp.text

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
    