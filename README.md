Introduction
============
TextMiner extracts values, lists and dicts from text.
It is mainly used to extract valuable information from web pages but can also be used on other text formats.

The machine way of extracting a piece of text from a web page is by specifying the start index and the end index.
Giving a piece of html `"<html><body>abc</body></html>"` and the text of interest "abc", we can do:

	start = html.find('<body>') + len('<body>')
	end = html.find('</body>', start)
	value = html[start:end]
	
For two values that may or may not exist? The code is something like this:

	start1 = html.find('<div id="value1">') + len('<div id="value1">')
	if start1 == -1:
	    end1 = 0
	    value1 = None
	else:
	    end1 = html.find('</div>', start1)
	    value1 = html[start1:end1]
	start2 = html.find('<div id="value2">') + len('<div id="value1">', end1)
	if start2 == -1:
	    value2 = None
	else:
	    end2 = html.find('</div>', start2)
	    value2 = html[start2:end2]
	
What if we need some type conversions?
What if we need some filters or transformations?
What if we want to extract from within the extracted values (a hierarchical extraction)?
The code quickly becomes tricky to write and difficult to understand.

What is the human way of expressing such a problem?
A human would say, I want the value between "`<body>`" and "`</body>`".
Or in [yaml](http://www.yaml.org/):

	value:
	  prefix: <body>
	  suffix: </body>

A more sophisticated example is:

	list:
	  prefix: <tr>
	  suffix: </tr>
	  dict:
	  - key: id
	    prefix: <td id="id">
	    suffix: </td>
	  - key: value
	    prefix: <td id="value">
	    suffix: </td>
	    type: int
	    
It means:

1. Extracts all values between "`<tr>`" and "`</tr>`" and form a list
2. For each list item, extract a string id (between "`<td id="id">`" and "`</td>`") and an int value (between "`<td id="value">`" and "`</td>`")

TextMiner enables you to extract values, lists and dicts from text by writing such yaml rules.

Installation
============
pip install textminer

Examples
========
**Extract a single value from html**

	import textminer
	
	html = '<html><body><div>abc</div></body></html>'
	rule = '''
	value:
	  prefix: <div>
	  suffix: </div>
	'''
	result = textminer.extract(html, rule)
	# result == 'abc'

**Extract a list from html**

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
	
**Extract a dict from html**

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

**Specify value type**

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
	
**Filters**

	import textminer
	
	html = '<html><body><div>123</div></body></html>'
	rule = '''
	value:
	  prefix: <body>
	  suffix: </body>
	  filters:
	  - stripHtml
	  - transform:
	    - float(value) / 100
	'''
	result = textminer.extract(html, rule)
	# result == 1.23

**Hierarchical extraction**

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
	