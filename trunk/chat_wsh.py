#!/usr/bin/env python
# -*- coding: utf-8 -*-
# chat_wsh.py

# Я предполагаю, что исходник находится в папке /pywebsocket-read-only/src/mod_pywebsocket
# msgutil служит для общения с внешним миром
from mod_pywebsocket import msgutil
#import msgutil
#import time

_GOODBYE_MESSAGE = 'Goodbye'

def web_socket_do_extra_handshake(request):
	# Принимаем всё
	pass
	
# Тут мы будем получать сообщения от браузера и слать серверу
def web_socket_transfer_data(request):
	# Бесконечно получаем сообщения
	while True:
		line = msgutil.receive_message(request)
		msgutil.send_message(request,
			time.strftime("%a, %d %b %Y %H:%M:%S +0000") + u': Тымц-тымц-тымц:' + line)
		if line == _GOODBYE_MESSAGE:
			return
def main():
	print "Trym Тымц-тымц-тымц\r"

if __name__ == "__main__":
	main()
