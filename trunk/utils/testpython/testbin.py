#!/usr/bin/python
# -*- coding: utf-8 -*-
# testbin.py

import httplib
import math
#import urllib

def dec2angleo(x, y):
	if x==0 and y==0:
		return -1.0
	if y==0:
		if x>0.0: return 270
		else: return 90
	theta = math.atan(y/x)
	theta = theta * 180 / math.pi
	if x>0.0:
		if y>0.0: return theta
		else: return 360 + theta
	else:
		return 180+theta

def dec2angle(x, y):
	if x==0 and y==0:
		return -1.0
	if y==0:
		if x>0.0: return 270
		else: return 90
	theta = math.atan(x/y)
	theta = theta * 180 / math.pi
	if y>0.0:
		if x>0.0: return 360-theta
		else: return -theta
	else:
		return 180-theta


def test(x, y):
	print "test(%6.3f, %6.3f) = %6.3f" % (x, y, dec2angle(x, y))

def main():
	test(0.0, 1.0)
	test(-1.0, 1.0)
	test(-1.0, 0.0)
	test(-1.0, -1.0)
	test(0.0, -1.0)
	test(1.0, -1.0)
	test(1.0, 0.0)
	test(1.0, 1.0)

	

if __name__ == "__main__":
	main()
