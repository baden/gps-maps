# -*- coding: utf-8 -*-

import os
import logging
from datetime import datetime, date, time, timedelta

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

#import datamodel
import datamodel2

DBGIMEI='111222333444555'

def SaveGPSPoint(userdb):
	#gpspoint = datamodel.DBGPSPoint(key_name = "gps_%s_%s" % (result.user.imei, datestamp.strftime("%Y%m%d%H%M%S")))
	#gpspoint = datamodel.DBGPSPoint()
	gpspoint = datamodel2.DBGPSPointC()
	gpspoint.user = userdb
	gpspoint.date = datetime.now()
	gpspoint.point = datamodel2.GPSPoint(lat=2.0)
	#gpspoint.latitude = 1.0
	#gpspoint.longitude = 1.0
	#gpspoint.sats = 1
	#gpspoint.fix = 1
	#gpspoint.speed = 1.0
	#gpspoint.course = 0.0
	#gpspoint.altitude = 0.0
	#gpspoint.vout = 0.0
	#gpspoint.vin = 0.0
	#gpspoint.in1 = 0.0
	#gpspoint.in2 = 0.0
	#gpspoint.fsource = 0
	return gpspoint
	#gpspoint.put()

def getuser():
	userdbq = datamodel2.DBUser.all().filter('imei =', DBGIMEI).fetch(1)
	if userdbq:
		userdb = userdbq[0]
	else:
		userdb = datamodel2.DBUser(key_name='IMEI_%s' % DBGIMEI, imei=DBGIMEI,phone='unknown',desc='nodesc')
		userdb.put()
	return userdb

class Benchmark(webapp.RequestHandler):
	def get(self):
		userdb = getuser()
		values = {}
		#values['pointscnt'] = datamodel.DBGPSPoint().all().filter('user =', userdb).count()
		#values['pointscnt'] = datamodel.DBGPSPoint2().all().filter('user =', userdb).count()
		#values['pointscnt'] = userdb.dbgpspoint2_set.count()
		values['pointscnt'] = userdb.geos_pack.count()
		#points = 
		values['points'] = userdb.geos_pack.fetch(10)
		path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.html')
		#self.response.headers['Content-Type']   = 'text/xml'
		self.response.out.write(template.render(path, values))


class PutData(webapp.RequestHandler):
	def get(self):
		#logging.info("   ===> Bencmark: put-data")
		#debuguser = 353358019726996
		userdb = getuser()
		
		cnt = int(self.request.get('cnt'))
		"""
		points = []
		for i in xrange(cnt):
			points.append(SaveGPSPoint(userdb))

		db.put(points)
		"""
		pdate = date.today()
		
		#logging.info("   ===> Bencmark: put-data: make two points")
		#points1 = datamodel2.GPSPoints()
		#points2 = datamodel2.GPSPoints()
		#logging.info("   ===> Bencmark: put-data: p1:%x(%x) p2:%x(%x)" % (id(points1), id(points1.points), id(points2), id(points2.points)))
		
		logging.info("   ===> Bencmark: put-data: datamodel2.DBGPSPointP.get_by_key_name")
		points = datamodel2.DBGPSPointP.get_by_key_name("t_%d_%d_%d" % (pdate.year, pdate.month, pdate.day))
		if points is None:
			logging.info("   ===> Bencmark: put-data: datamodel2.DBGPSPointP")
			points = datamodel2.DBGPSPointP(key_name="t_%d_%d_%d" % (pdate.year, pdate.month, pdate.day))
			points.user = userdb
			points.date = pdate
			points.points = datamodel2.GPSPoints()
		#logging.info("   ===> Bencmark: put-data: datamodel2.GPSPoints")
		#points.points = datamodel2.GPSPoints()
		
		now = datetime.now()
		
		for i in xrange(cnt):
			points.points.append(time(hour=now.hour, minute=now.minute, second=now.second), lat=1.0, lon=2.0, sats=3)
			now = now + timedelta(seconds=1)
		#points.points.append(time(hour=now.hour, minute=now.minute, second=now.second), lat=1.0, lon=2.0, sats=3)
		#oints.points.append(time(hour=now.hour, minute=now.minute, second=now.second), lat=1.0, lon=2.0, sats=3)
		
		logging.info("   ===> Bencmark: put-data: points.put")
		points.put()
		#for point in points:
		#	point.put()
		
		logging.info("   ===> Bencmark: put-data (%d)" % cnt)
		self.redirect("/benchmark")

class PurgeData(webapp.RequestHandler):
	def get(self):
		#logging.info("   ===> Bencmark: put-data")
		#debuguser = 353358019726996
		userdb = getuser()
		
		#cnt = int(self.request.get('cnt'))
		cnt = 200
		
		#q = userdb.geos
		#db.delete(userdb.geos(keys_only=True).fetch(cnt))
		db.delete(userdb.geos_pack.fetch(cnt))
		#db.delete(userdb.dbgpspoint2_set.fetch(cnt))
		#db.delete(userdb.geos)
		
		logging.info("   ===> Bencmark: purge-data (%d)" % cnt)
		self.redirect("/benchmark")

application = webapp.WSGIApplication(
	[
		('/benchmark/put-data.*', PutData),
		#('/benchmark/list-data.*', ListData),
		('/benchmark/purge-data.*', PurgeData),
		('/benchmark.*', Benchmark),
	],
	debug=True
)

def main():
	#print "Content-type: text"
	#print
	#print "Hello, world!!!"
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
