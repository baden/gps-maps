# -*- coding: utf-8 -*-

from datetime import date, timedelta, datetime

#ZERO = timedelta(0)
TIMEZONE = timedelta(hours =+ 2)
HOUR = timedelta(hours = 1)
SAVEDAYLIGHT = True

def _FirstSunday(dt):
	"""First Sunday on or after dt."""
	return dt + timedelta(days=(6-dt.weekday()))

def fromUTC(utctime):
	if SAVEDAYLIGHT:
		# 2 am on the second Sunday in March
		dst_start = _FirstSunday(datetime(utctime.year, 3, 8, 2))
		# 1 am on the first Sunday in November
		dst_end = _FirstSunday(datetime(utctime.year, 11, 1, 1))

		if dst_start <= utctime < dst_end:
			return utctime + TIMEZONE + HOUR
		else:
	        	return utctime + TIMEZONE
	        
	else:
	        return utctime + TIMEZONE

def toUTC(localtime):
	if SAVEDAYLIGHT:
		# 2 am on the second Sunday in March
		dst_start = _FirstSunday(datetime(localtime.year, 3, 8, 2))
		# 1 am on the first Sunday in November
		dst_end = _FirstSunday(datetime(localtime.year, 11, 1, 1))

		if dst_start <= localtime < dst_end:
			return localtime - TIMEZONE - HOUR
		else:
	        	return localtime - TIMEZONE
	        
	else:
	        return localtime - TIMEZONE
