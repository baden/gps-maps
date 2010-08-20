#!/usr/bin/python
# -*- coding: utf-8 -*-
# testbin.py

import httplib

def senddata(id):
	body = """
gps.T1.1	INT	600	600
gps.T1.0	INT	30	30
gps.B1.3	INT	512	512
gps.B1.2	INT	512	512
gps.B1.1	INT	512	512
gps.B1.0	INT	512	512
gps.A1.2	INT	5	5
gps.A1.3	INT	15	15
gps.A1.0	INT	5	5
gps.A1.1	INT	10	10
akkum.I.1	INT	15	15
akkum.I.0	INT	3	3
akkum.I.3	INT	0	0
akkum.I.2	INT	9	9
gps.T5.1	INT	120	120
gps.T5.0	INT	60	60
gps.T5.3	INT	240	240
gps.T5.2	INT	60	60
gps.S1.0	INT	100	100
gps.S1.1	INT	1000	1000
gps.S1.2	INT	100	100
gps.S1.3	INT	1000	1000
gps.T3.3	INT	240	240
gps.T3.2	INT	10	10
gps.T3.1	INT	120	120
gps.T3.0	INT	10	10
gps.T2.2	INT	1	1
gps.T2.3	INT	60	60
gps.T2.0	INT	1	1
gps.T2.1	INT	60	60
adc.U.0	INT	202	202	
adc.U.1	INT	337	337	
gps.T1.3	INT	600	600	
gps.T1.2	INT	10	10	
gps.T0.0	INT	10	10	
gps.T0.1	INT	10	10	
gps.T0.2	INT	10	10	
gps.T0.3	INT	10	10	
akkum.U.1	INT	907	907	
akkum.U.0	INT	862	862	
akkum.U.3	INT	984	984	
akkum.U.2	INT	911	911	
akkum.U.4	INT	911	911	
gps.V0.2	INT	10	10	
gps.V0.3	INT	20	20	
gps.V0.0	INT	5	5	
gps.V0.1	INT	20	20	
gps.T4.0	INT	720	720
gps.T4.1	INT	240	240
gps.T4.2	INT	720	720
gps.T4.3	INT	120	120
		"""
	
#	headers = {"Content-type": "text/plain", #"application/octet-stream",
#		"Content-Length": "%d" % len(body)}

	headers = {"Content-Type": "text/plain"}

#	headers = {"Content-Type": "application/x-www-form-urlencoded"}

	conn = httplib.HTTPConnection("127.0.0.1:80")
	#conn = httplib.HTTPConnection("127.0.0.1:8080")
	#conn = httplib.HTTPConnection("gps-maps.appspot.com:80")
	#conn.set_debuglevel(1)
	conn.request("POST", "/config?cmd=save&imei=353358016204857", body, headers)
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
