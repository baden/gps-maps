#!/usr/bin/python
# -*- coding: utf-8 -*-
# testbin.py

import httplib

def senddata(id):
	#body = open("getbin", "rb").read()

	body = "\xFF\xF2\x20\x13\x06\x11\x29\x2D\x10\x10\x24\x22\x26\x24\x12\x03\x04\x04\x11\x04\xAE\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x22"
	#body = "\xFF\xF2\x20\xF0\xF0\xF0\x29\x2D\x10\x10\x24\x22\x26\x24\x12\x03\x04\x04\x11\x04\xAE\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x22"
	
	headers = {"Content-type": "application/octet-stream",
		"Content-Length": "%d" % len(body)}

	conn = httplib.HTTPConnection("127.0.0.1:80")
	#conn = httplib.HTTPConnection("127.0.0.1:8080")
	#conn = httplib.HTTPConnection("gps-maps.appspot.com:80")
	#conn.set_debuglevel(1)
	conn.request("POST", "/bingps?imei=123456789013&dataid=%d&phone=322322&desc=Opisanie" % id, body, headers)
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
