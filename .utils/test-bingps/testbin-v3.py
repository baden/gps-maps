#!/usr/bin/python
# -*- coding: utf-8 -*-
# testbin.py

import httplib

import socket

HOST = "127.0.0.1"
PORT = 80
#HOST = "gps-maps.appspot.com"
#PORT = 80
#HOST = "212.110.139.65"
#PORT = 8015

SYS = 2
IMAGE = "binbackup (1000)"
IMEI = ("0", "356895035376246", "356895035358996", "353358016204856", "356895035359317")
#IMEI = ("0", "35689503537624601", "35689503535899601", "35335801620485601")	#Fake

def senddatav2(id):
	if SYS>4:
		print("Support SYS=[1,3]. fail")
		return
	
	body = open("gps%d/%s" % (SYS, IMAGE), "rb").read()
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print("Connect to %s:%d" % (HOST, PORT))
	s.connect((HOST, PORT))

	send = "POST /bingps?imei=%s&dataid=%d HTTP/1.1\r\n" % (IMEI[SYS], id)
	send+= "Host: gps-maps.appspot.com\r\n"
	send+= "Content-type: application/octet-stream\r\n"
	send+= "Content-Length: %d\r\n" % len(body)
	send+= "\r\n"
	#send+= body

	print(send)
	print("{BODY}\n")

	s.send(send)
	s.send(body)
	print("Wait answer...\n");
	while 1:
		s.settimeout(5.0);
		try:
			received = s.recv(1024)
		except:
			print('-timeout-')
			break
		if received:
			print received
			if received.find("BINGPS: OK")>0:
				print("-ok-")
				break
		else:
			print("-none-")
			break
			#if received.startswith("B"): break
	s.close()
	print("OK\n")

def senddata(id):
	body = open("gps3/binbackup (0)", "rb").read()

	#body = "\xFF\xF2\x20\x13\x06\x11\x29\x2D\x10\x10\x24\x22\x26\x24\x12\x03\x04\x04\x11\x04\xAE\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x22"
	#body = "\xFF\xF2\x20\xF0\xF0\xF0\x29\x2D\x10\x10\x24\x22\x26\x24\x12\x03\x04\x04\x11\x04\xAE\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x22"
	
	headers = {"Content-type": "application/octet-stream",
		"Content-Length": "%d" % len(body)}

	#conn = httplib.HTTPConnection("127.0.0.1:80")
	#conn = httplib.HTTPConnection("127.0.0.1:8080")
	#conn = httplib.HTTPConnection("gps-maps.appspot.com:80")
	conn = httplib.HTTPConnection("212.110.139.65:8015")

	conn.set_debuglevel(1)
	conn.request("POST", "/bingps?imei=353358016204856&dataid=%d" % id, body, headers)
	response = conn.getresponse()
	print response.status, response.reason
	data = response.read()
	conn.close()
	print data

def main():
	print('--------------------------------------------------------------------')

#	senddata(0)
#	senddata(1)
	senddatav2(0)
	

if __name__ == "__main__":
	main()
