# -*- coding: utf-8 -*-
import serial


ser = serial.Serial(0)  # open first serial port
# ser = serial.Serial('COM7', timeout=0.5) for Windows
# ser.readall()
print ser.portstr       # check which port was really used
ser.write("hello")      # write a string
ser.close()             # close port




"""
Из статьи про проверку счета пример:

Возможно зависит от модема, но в моем телефоне (Philips) в ответах используется кодировка UCS2. Я на питоне делаю так:
>>> import serial
>>> ser = serial.Serial('COM7', timeout=0.5)
>>> ser.write('AT+CUSD=1,"*102#"\r\n')
19L
>>> hexstr = ser.readall().split(',')[1][1:-1]
>>> response = hexstr.decode('hex').decode('utf-16-be')
>>> print response.encode('cp866', 'ignore') # windows cmd
Баланс 299,43 руб. Сумма бонуса 0.30 руб.

"""


"""
Или вот /не про serial, но на ту же тему/ (http://habrahabr.ru/blogs/telecom/98846/):

#!/usr/bin/python
import binascii
import sys
f = open("/dev/ttyUSB2", "r+")
data=''
error="Usage: python ussd.py action (code)\r\nActions: balans, popolnit, data-status, 3g-data-status, signal"
if len(sys.argv) < 2:
    print error
    sys.exit()
 
if sys.argv[1] == 'balans':
    print>>f, "AT+CUSD=1,*111#,15\r\n"
    while data[:5]!="+CUSD":
        data=f.readline()
    data = data[10:-6]
    print binascii.unhexlify(data)
elif sys.argv[1] == 'signal':
    print>>f, "AT+CSQ\r\n"
    while data[:5]!="+CSQ:":
        data=f.readline()
    data = data[6:-5]
    sig_str = -113+int(data)*2
    sig_per = int(data)*100 / 31
    print unicode(sig_str)+"dBm / "+unicode(sig_per)+"%"
elif sys.argv[1] == 'popolnit':
    print>>f, "AT+CUSD=1,*123*"+sys.argv[2]+"#,15\r\n"
    while data[:5]!="+CUSD":
        data=f.readline()
    data = data[10:-6]
    print binascii.unhexlify(data)
elif sys.argv[1] == 'data-status':
    print>>f, "AT+CUSD=1,*121#,15\r\n"
    while data[:5]!="+CUSD":
        data=f.readline()
    data = data[10:-6]
    print binascii.unhexlify(data)
elif sys.argv[1] == '3g-data-status':
    print>>f, "AT+CUSD=1,*122#,15\r\n"
    while data[:5]!="+CUSD":
        data=f.readline()
    data = data[10:-6]
    print binascii.unhexlify(data)
else:
    print error
f.close
"""