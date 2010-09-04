#!/usr/bin/python
# -*- coding: utf-8 -*-
# testbin.py

import httplib

def senddata(id):
	

	#conn = httplib.HTTPConnection("127.0.0.1:80")
	#conn = httplib.HTTPConnection("127.0.0.1:8080")
	conn = httplib.HTTPConnection("gps-maps.appspot.com:80")

	#body = "SWID: 3034"
	body = ""
	headers = {"Accept-Encoding": "identity,gzip,compress,deflate", "Content-Length": "%d" %len(body)}

	#conn.set_debuglevel(1)
	#conn.request("GET", "/firmware?cmd=get&hwid=3031", body, headers)
	conn.request("GET", "/firmware?cmd=check&hwid=3031", body, headers)
	response = conn.getresponse()
	#print response.status, response.reason
	data = response.read()
	conn.close()
	print data

def main():
	senddata(0)
#	senddata(1)
	

if __name__ == "__main__":
	main()
