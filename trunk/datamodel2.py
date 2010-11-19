# -*- coding: utf-8 -*-

import logging
import zlib

from google.appengine.ext import db

from local import fromUTC
from datetime import time

from sorteddict import sorteddict

import struct

class DBUser(db.Model):
	#userid = db.IntegerProperty()			# Unique
	imei = db.StringProperty(multiline=False)	# IMEI
	phone = db.StringProperty(multiline=False)	# Phone number, for example: +380679332332
	password = db.StringProperty(multiline=False)	# User password
	date = db.DateTimeProperty(auto_now_add=True)	# Registration date
	desc = db.StringProperty(multiline=False)	# Описание
	#icon = db.


FSOURCE = {
	0: "-",
	1: "SUDDENSTOP",
	2: "STOPACC",
	3: "TIMESTOPACC",
	4: "SLOW",
	5: "TIMEMOVE",
	6: "START",
	7: "TIMESTOP",
	8: "ANGLE",
	9: "DELTALAT",
	10: "DELTALONG",
	11: "DELTA",
}

class GPSPoint(object):
	def __init__(self, lat=0.0, lon=0.0, sats=0, speed=0.0, cource=0.0, vout=0.0, vin=0.0, fsource=0):
		self.lat = lat
		self.lon = lon
		self.sats = sats
		self.speed = speed
		self.cource = cource
		self.vout = vout
		self.vin = vin
		self.fsource = fsource
	def __str__(self):
		return '{lat:%.6f,lon:%.6f}' % (self.lat, self.lon)


class GPSPointProperty(db.Property):
	data_type = GPSPoint
	# For writing to datastore.
	def get_value_for_datastore(self, model_instance):
		point = super(GPSPointProperty, self).get_value_for_datastore(model_instance)
		pack = struct.pack('ffifffff',
			point.lat, point.lon, point.sats, point.speed, point.cource, point.vout, point.vin, point.fsource)
		return pack
	# For reading from datastore.
	def make_value_from_datastore(self, value):
		if value is None:
			return None
		u = struct.unpack('ffifffff', value)
		return GPSPoint(
			lat=u[0], lon=u[1], sats=u[2], speed=u[3], cource=u[4], vout=u[5], vin=u[6], fsource=u[7]
		)
	def validate(self, value):
		if value is not None and not isinstance(value, GPSPoint):
			raise BadValueError('Property %s must be convertible '
				'to a GPSpoint instance (%s)' % (self.name, value))
		return super(GPSPointProperty, self).validate(value)
	def empty(self, value):
		return not value

class GPSPoints(object):
	def __init__(self, points = None):
		if points is not None:
			self.points = points
		else:
			self.points = sorteddict({})
		logging.info("   ===> GPSPoints: __init__ (%x:%s)" % (id(self.points), self.points))
	#def append(self, ptime, point):
	#	self.points[ptime] = point 
	def append(self, ptime, lat=0.0, lon=0.0, sats=0, speed=0.0, cource=0.0, vout=0.0, vin=0.0, fsource=0):
		self.points[ptime] = dict({'lat': lat, 'lon':lon, 'sats':sats, 'speed':speed, 'cource':cource, 'vout':vout, 'vin':vin, 'fsource':fsource}) 
		#logging.info("   ===> GPSPoints: append (%x:%s)" % (id(self.points), self.points))
	def count(self):
		return len(self.points)
	def __str__(self):
		return '%d:%s' % (len(self.points), self.points)


PACK_STR = 'BBBBffffffBBBBii'
PACK_LEN = 40
		
class GPSPointsProperty(db.Property):
	data_type = GPSPoints
	# For writing to datastore.
	def get_value_for_datastore(self, model_instance):
		#print("Content-Type: text/html\r\n")
		#print("aaaaaaaaaa bbbbbbb<br/>")
		points = super(GPSPointsProperty, self).get_value_for_datastore(model_instance)
		pack = 'HDR:'
		#print(points.points)
		#print("<br />")
		#print('item ', points.points)
		for k, v in points.points.items():
			#print(k)
			#print(v)
			#print("<br />")
			#pack += struct.pack('bbbbffiffffiiiiiiii',
			#logging.info("%d-%d-%d-%d-%f-%f-%f-%f-%f-%f-%d-%d-%d-%d-%d-%d" % (
			#	k.hour, k.minute, k.second, v['sats'],		# 4 байта
			#	v['lat'], v['lon'], v['speed'], v['cource'], v['vout'], v['vin'], # 6 float
			#	v['fsource'], 0, 0, 0,	# 4 байта
			#	0, 0	# Резерв 2 int
			#))
			pack += struct.pack(PACK_STR,
				k.hour, k.minute, k.second, v['sats'],		# 4 байта
				v['lat'], v['lon'], v['speed'], v['cource'], v['vout'], v['vin'], # 6 float
				v['fsource'], 0, 0, 0,	# 4 байта
				0, 0	# Резерв 2 int
			)
		#return db.Blob(pack)
		logging.info("   ===> GPSPointsProperty: get_value_for_datastore(u:%d)" % len(pack))
		compressed = zlib.compress(pack, 9)
		logging.info("   ===> GPSPointsProperty: get_value_for_datastore (c:%d)" % len(compressed))
		#return db.Blob(zlib.compress(pack, 9))
		return db.Blob(compressed)

	# For reading from datastore.
	def make_value_from_datastore(self, value):
		logging.info("   ===> GPSPointsProperty: make_value_from_datastore")
		r = GPSPoints()
		if value is None:
			return r
		value = zlib.decompress(value)
		l = len(value)
		#ss = "%d -" % l
		#for c in value:
		#	ss += " %02X" % ord(c)
		#print(ss)
		if l<(PACK_LEN+4):
			return r
		#for i in xrange(int((l-4) / 64)):
		for i in xrange(int((l-4) / PACK_LEN)):
			#print(i*36+4)
			#print(i)
			#u = struct.unpack('bbbbffiffffiiiiiiii', value[i*64+4:i*64+4+64])
			#u = struct.unpack(PACK_STR, value[i*64+4:i*64+4+64])
			u = struct.unpack(PACK_STR, value[i*PACK_LEN+4:i*PACK_LEN+4+PACK_LEN])
			r.append(
				time(u[0], u[1], u[2]),
				lat=u[4], lon=u[5], sats=u[3], speed=u[6], cource=u[7], vout=u[8], vin=u[9], fsource=u[10]
			)
		return r
	def validate(self, value):
		if value is not None and not isinstance(value, GPSPoints):
			raise BadValueError('Property %s must be convertible '
				'to a GPSpoints instance (%s)' % (self.name, value))
		return super(GPSPointsProperty, self).validate(value)
	def empty(self, value):
		return not value
		
class DBGPSPointC(db.Model):
	user = db.ReferenceProperty(DBUser, collection_name='geos2')
	date = db.DateTimeProperty(name='c')
	point = GPSPointProperty()

class DBGPSPointP(db.Model):
	user = db.ReferenceProperty(DBUser, collection_name='geos_pack')
	#date = db.DateProperty(name='d')
	date = db.DateProperty()
	#points = GPSPointsProperty(name='p')
	points = GPSPointsProperty()
	@property
	def size(self):
		return 123

# Новая модель без использования наследования db.Property.
# При таком подходе немного больше работы, но упрощаются простые запросы вроде, подсчета количества точек.

# Пример использования.
# 1. Добавление записи.
#  При добавлении записи, предварительно запрашивается дневной пакет по дате точки.
#   day = userdb.geos_daypack.get()


class DBGPSPointDP(db.Model):
	user = db.ReferenceProperty(DBUser, collection_name='geos_daypack')
	#date = db.DateProperty(name='d')
	date = db.DateProperty()
	#points = GPSPointsProperty(name='p')
	#points = GPSPointsProperty()
	#raw = db.BlobProperty()
	#raw = db.ListProperty(db.ReferenceProperty(DBUser))
	@property
	def points(self):
		return sorteddict({})
	@staticmethod
	def pack(self):
		pass

class DBGPSDateList(db.Model):
	user = db.ReferenceProperty(DBUser, collection_name='geos_dates')
	date = db.DateProperty()

class DBmulti(db.Model):
	date = db.DateProperty()
	rvalue = db.ListProperty(str)
