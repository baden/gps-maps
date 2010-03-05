#!/usr/bin/python
# -*- coding: utf-8 -*-
# testbin.py

import httplib
#import urllib

def main():
	text = "abcdefghijklmnopqrstuvwxyz"
	print text

	while len(text)>0:
		print text[:8]
		text = text[8:]
		#print text
	#print text

	

if __name__ == "__main__":
	main()
