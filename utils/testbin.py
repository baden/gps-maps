#!/usr/bin/python
# -*- coding: utf-8 -*-
# testbin.py

import httplib

def senddata(id):
	body = open("getbin", "rb").read()

	#body = "\xF2\x13\x06\x11\x29\x2D\xF0\xF0\x24\x22\x26\x24\x12\x03\x04\x04\x11\x04\xAE\x40\x00\x00\xFF\xFF"
	
	headers = {"Content-type": "application/octet-stream",
		"Content-Length": "%d" % len(body)}

	conn = httplib.HTTPConnection("127.0.0.1:80")
	#conn = httplib.HTTPConnection("127.0.0.1:8080")
	#conn = httplib.HTTPConnection("gps-maps.appspot.com:80")
	#conn.set_debuglevel(1)
	conn.request("POST", "/bingeos?imei=353358016204857&dataid=%d" % id, body, headers)
	response = conn.getresponse()
	print response.status, response.reason
	data = response.read()
	conn.close()
	print data

def main():
	print('--------------------------------------------------------------------')

	senddata(0)
#	senddata(1)
	

if __name__ == "__main__":
	main()
