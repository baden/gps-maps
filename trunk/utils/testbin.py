#!/usr/bin/python
# -*- coding: utf-8 -*-
# testbin.py

import httplib
#import urllib

def senddata(id):
#	body = ""
	
#	body += "\x58\x13\x23\x02\xDB\x24\x03\x07\x01\x45\x1B\x58\x06"
#	for j in range(1):
		#          H   0   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  17  18  19  20  C   C
#		body += "\xF2\x1D\x01\x10\x14\x13\x18\x30\x58\x23\x30\x02\xDB\x24\x00\x03\x07\x01\x45\x1B\x58\x06\xFF\xFF"
#	body += "\xF2\x1D\x01\x10\x14\x13\x30\x18\x00"
	
	body = open("getbin", "rb").read()
#	print len(body)

#	return
	
	headers = {"Content-type": "application/octet-stream",
		"Content-Length": "%d" % len(body)}

	#conn = httplib.HTTPConnection("127.0.0.1:80")
	#conn = httplib.HTTPConnection("127.0.0.1:8080")
	conn = httplib.HTTPConnection("gps-maps.appspot.com:80")
	#conn.set_debuglevel(1)
	conn.request("POST", "/bingeos?imei=123456789013&dataid=%d" % id, body, headers)
	response = conn.getresponse()
	print response.status, response.reason
	data = response.read()
	conn.close()
	print data

def main():
	print('--------------------------------------------------------------------')
	#params = urllib.urlencode({'spam': 1, 'eggs': 2, 'bacon': 0})

	senddata(0)
#	senddata(1)
	

if __name__ == "__main__":
	main()
