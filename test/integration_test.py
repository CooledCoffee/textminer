# -*- coding: utf-8 -*-
from textminer.util import Dict
from unittest.case import TestCase
import textminer
import urllib2

class ExtractFromUrlTest(TestCase):
    def setUp(self):
        self._old_url_open = urllib2.urlopen
        html = '''
<html>
<body>
<h1>title</h1>
<table>
    <tr>
        <td>001</td>
        <td>123</td>
    </tr>
    <tr>
        <td>002</td>
        <td>321</td>
    </tr>
</table>
</body>
</html>
'''
        def _urlopen(url, timeout=None):
            return Dict(read=lambda: html)
        urllib2.urlopen = _urlopen
        super(ExtractFromUrlTest, self).setUp()
        
    def tearDown(self):
        urllib2.urlopen = self._old_url_open
        super(ExtractFromUrlTest, self).tearDown()
        
    def test(self):
        rule = '''
dict:
- key: title
  prefix: <h1>
  suffix: </h1>
- key: items
  prefix: <table>
  suffix: </table>
  list:
    prefix: <tr>
    suffix: </tr>
    dict:
    - key: id
      prefix: <td>
      suffix: </td>
    - key: value
      prefix: <td>
      suffix: </td>
      type: int
'''
        result = textminer.extract_from_url('http://test.com/test', rule)
        self.assertEquals('title', result['title'])
        self.assertEquals(2, len(result['items']))
        self.assertEquals('001', result['items'][0]['id'])
        self.assertEquals(123, result['items'][0]['value'])
        self.assertEquals('002', result['items'][1]['id'])
        self.assertEquals(321, result['items'][1]['value'])
        