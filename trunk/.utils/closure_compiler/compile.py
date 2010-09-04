#!/usr/bin/python2.4

import httplib, urllib, sys

# Define the parameters for the POST request and encode them in
# a URL-safe format.

body = open(sys.argv[1], "rt").read()

params = urllib.urlencode([
    ('js_code', body),
    ('output_format', 'text'),
    ('compilation_level', 'ADVANCED_OPTIMIZATIONS'),
    ('output_info', 'compiled_code'),
    #('output_info', 'warnings'),
    ('output_info', 'errors'),
    #('output_info', 'statistics'),
    #('warning_level', 'verbose'),
    #('js_externs', 'function sayHi(){}'), # <-- New parameter!
    #('formatting', 'pretty_print'),
    ('use_closure_library', 'true'),
  ])

# Always use the following value for the Content-type header.
headers = { "Content-type": "application/x-www-form-urlencoded" }
conn = httplib.HTTPConnection('closure-compiler.appspot.com')
conn.request('POST', '/compile', params, headers)
response = conn.getresponse()
data = response.read()
print data
conn.close
