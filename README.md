Introduction
============
Textminer extracts values, lists and dicts from text.
It works on all text formats and is heavily used on html pages.

Giving a piece of html

	<html>
	<body>
	<div id="value1">111</div>
	...
	<div id="value2">222</div>
	</body>
	</html>
	
The usual way of extracting the two values "111" and "222" is:

	start1 = html.find('<div id="value1">') + len('<div id="value1">')
	if start1 == -1:
	    end1 = 0
	    value1 = None
	else:
	    end1 = html.find('</div>', start1)
	    value1 = html[start1:end1]
	    value1 = int(value1)
	start2 = html.find('<div id="value2">') + len('<div id="value1">', end1)
	if start2 == -1:
	    value2 = None
	else:
	    end2 = html.find('</div>', start2)
	    value2 = html[start2:end2]
	    value2 = int(value2)

The textminer's way of doing the same thing is:

	import textminer
	
	rule = '''
	dict:
	- key: value1
	  prefix: <div id="value1">
	  suffix: </div>
	  type: int
	- key: value2
	  prefix: <div id="value2">
	  suffix: </div>
	  type: int
	'''
	results = textminer.extract(html, rule)

Textminer uses <a href="http://www.yaml.org/" target="_blank">yaml</a> to define rules, which is far more clear and expressive.
This enables you to write very complicated rule for hierarchical extraction (see below).

Installation
============
pip install textminer

or

easy_install textminer

Try it yourself
===============

You can test your rules <a href="http://cs-textminer.appspot.com/" target="_blank">here</a>.

Basic Usage
===========
### Extract a single value from html ###

	import textminer
	
	html = '<html><body><div>abc</div></body></html>'
	rule = '''
	value:
	  prefix: <div>
	  suffix: </div>
	'''
	result = textminer.extract(html, rule)
	# result == 'abc'

### Extract a list from html ###

	import textminer
	
	html = '''
	<html>
	<body>
	<ul>
		<li>aaa</li>
		<li>bbb</li>
		<li>ccc</li>
	</ul>
	</body>
	</html>
	'''
	rule = '''
	list:
	  prefix: <li>
	  suffix: </li>
	'''
	result = textminer.extract(html, rule)
	# result == ['aaa', 'bbb', 'ccc']
	
### Extract a dict from html ###

	import textminer
	
	html = '''
	<html>
	<body>
	<div id="code">001</div>
	<div id="value">123</div>
	</body>
	</html>
	'''
	rule = '''
	dict:
	- key: code
	  prefix: <div id="code">
	  suffix: </div>
	- key: value
	  prefix: <div id="value">
	  suffix: </div>
	'''
	result = textminer.extract(html, rule)
	# result == {'code': '001', 'value': '123'}

Note that the fields in the rule should be in the order they appear in the html.

### Specify value type ###

	import textminer
	
	html = '<html><body><div>123</div></body></html>'
	rule = '''
	value:
	  prefix: <div>
	  suffix: </div>
	  type: int
	'''
	result = textminer.extract(html, rule)
	# result == 123
	
### Hierarchical extraction ###

The real power of textminer is to do hierarchical extraction.

	import textminer
	
	html = '''
	<html>
	<body>
	<h1>Test Page</h1>
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
	      type: int
	'''
	result = textminer.extract(html, rule)
	# result == {
	#     'title': 'Test Page',
	#     'items': [
	#         {'code': '001', 'value': 123},
	#         {'code': '002', 'value': 321}
	#     ]
	# }
	
### Extract from a url ###

Since textminer is heavily used on web pages.
It provides a utility function extract_from_url to download html and extract from it.
This saves you a few lines of code.

	import textminer
	
	rule = '''
	value:
	  prefix: <title>
	  suffix: </title>
	'''
	textminer.extract_from_url('http://www.google.com/', rule)

Advanced Usage
==============
### Filters ###

	import textminer
	
	html = '<html><body><div>1<b>2</b>3</div></body></html>'
	rule = '''
	value:
	  prefix: <div>
	  suffix: </div>
	  filters:
	  - stripHtml
	  - transform:
	    - float(value) / 100
	'''
	result = textminer.extract(html, rule)
	# result == 1.23
	
### Regular expressions for prefix & suffix ###

Regular expressions are denoted by "/" before and after the string.

	import textminer
	
	html = '<html><body><div sessionId="123456789">aaa</div></body></html>'
	rule = '''
	value:
	  prefix: /<div sessionId="\\d+">/
	  suffix: </div>
	'''
	result = textminer.extract(html, rule)

### Using rules of other formats ###

Yaml is perfect for the rules, but textminer also supports json and raw python dict.

	import textminer
	
	html = '<html><body><div>123</div></body></html>'
	
	python_rule = {'value': {'prefix': '<body>', 'suffix': '</body>'}}
	result = textminer.extract(html, python_rule, fmt=None)
	
	json_rule = '{"value": {"prefix": "<body>", "suffix": "</body>"}}'
	result = textminer.extract(html, json_rule, fmt='json')
	
Python3 Support
===============
Textminer is tested under python 2.7 and python 3.3.
