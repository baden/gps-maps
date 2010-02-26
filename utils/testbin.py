#!/usr/bin/python
# -*- coding: utf-8 -*-
# testbin.py

import httplib
#import urllib


def main():
	print('--------------------------------------------------------------------')
	#params = urllib.urlencode({'spam': 1, 'eggs': 2, 'bacon': 0})
	
	body = ""
	
	body += "\x23\x02\xDB\x24\x03\x07\x01\x45\x1B\x58\x06"
	for j in range(2):
		body += "\xF2\x1D\x01\x10\x14\x13\x30\x18\x00\x58\x13\x23\x02\xDB\x24\x03\x07\x01\x45\x1B\x58\x06"
	body += "\xF2\x1D\x01\x10\x14\x13\x30\x18\x00"
	
	headers = {"Content-type": "application/octet-stream",
		"Content-Length": "%d"%len(body)}

	conn = httplib.HTTPConnection("127.0.0.1:80")
	#conn = httplib.HTTPConnection("127.0.0.1:8080")
	#conn = httplib.HTTPConnection("gps-maps.appspot.com:80")
	#conn.set_debuglevel(1)
	conn.request("POST", "/bingeos?imei=123456789013&dataid=0", body, headers)
	response = conn.getresponse()
	print response.status, response.reason
	data = response.read()
	conn.close()
	print data

if __name__ == "__main__":
	main()
