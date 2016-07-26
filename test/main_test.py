# -*- coding: utf-8 -*-
from requests.exceptions import HTTPError
from textminer import main
from textminer.errors import MinerError
from unittest.case import TestCase
import six
if six.PY2:
    from StringIO import StringIO  # @UnusedImport
else:
    from io import BytesIO as StringIO  # @Reimport

class ExtractTest(TestCase):
    def test_success(self):
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
        
    def test_error(self):
        html = '<html>...</html>'
        rule = '''
value:
  prefix: <html>
  suffix: </html>
  filters:
  - int
'''
        with self.assertRaises(MinerError):
            main.extract(html, rule)
        
class ExtractFromUrlTest(TestCase):
    def test_normal(self):
        rule = '''
value:
  prefix: 'lang="'
  suffix: '"'
'''
        value = main.extract_from_url('http://www.ebay.com/', rule)
        self.assertEquals('en', value)
        
    def test_error(self):
        with self.assertRaises(HTTPError):
            main.extract_from_url('http://www.ip138.com/abc', '')
        