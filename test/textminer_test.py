# -*- coding: utf-8 -*-
from requests.exceptions import HTTPError
from textminer import util, main
from textminer.util import Dict
from unittest.case import TestCase

class ExtractTest(TestCase):
    def test(self):
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
      filters:
      - int
'''
        result = main.extract(html, rule)
        self.assertEquals('title', result['title'])
        self.assertEquals(2, len(result['items']))
        self.assertEquals('001', result['items'][0]['id'])
        self.assertEquals(123, result['items'][0]['value'])
        self.assertEquals('002', result['items'][1]['id'])
        self.assertEquals(321, result['items'][1]['value'])
        
class ExtractFromUrlTest(TestCase):
    def test_normal(self):
        rule = '''
value:
  prefix: <title>
  suffix: </title>
'''
        value = main.extract_from_url('http://www.name.com', rule)
        self.assertIn('Domain Names', value)
        
    def test_error(self):
        with self.assertRaises(HTTPError):
            main.extract_from_url('http://www.amazon.com/abc', '')
        