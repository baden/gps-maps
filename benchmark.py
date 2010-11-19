# -*- coding: utf-8 -*-

import os
import logging
import random
from datetime import datetime, date, time, timedelta
import time

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api.labs import taskqueue

from django.utils import simplejson as json

#import datamodel
import datamodel2

from local import toUTC, fromUTC

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
		values['points'] = userdb.geos_pack.order("-date").fetch(30)	# Последние 30 штук (месяц)
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
		pdate = date.today() + timedelta(days=int(self.request.get('day', default_value="0")))
	
		
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

		if cnt == -1:
			for h in xrange(24):
				for m in xrange(60):
					for s in xrange(60):
						points.points.append(
							time(hour=h, minute=m, second=s),
							lat = random.uniform(-90.0, 90.0),
							lon = random.uniform(-180.0,180.0),
							sats = random.randint(0,255),
							speed = random.uniform(0.0, 260.0),
							cource = random.uniform(0.0, 360.0),
							vout = random.uniform(0.0, 36.0),
							vin = random.uniform(0.0, 6.0),
							fsource = random.randint(0,255),
						)
		elif cnt == -2:
			for h in xrange(24):
				for m in xrange(60):
					for s in xrange(10):
						points.points.append(
							time(hour=h, minute=m, second=s),
							lat = random.uniform(-90.0, 90.0),
							lon = random.uniform(-180.0,180.0),
							sats = random.randint(0,255),
							speed = random.uniform(0.0, 260.0),
							cource = random.uniform(0.0, 360.0),
							vout = random.uniform(0.0, 36.0),
							vin = random.uniform(0.0, 6.0),
							fsource = random.randint(0,255),
						)
		else:
			for i in xrange(cnt):
				points.points.append(time(hour=now.hour, minute=now.minute, second=now.second), lat=random.uniform(-90.0, 90.0), lon=random.uniform(-180.0, 180.0), sats=random.randint(0,255))
				now = now + timedelta(seconds=1)
		#points.points.append(time(hour=now.hour, minute=now.minute, second=now.second), lat=1.0, lon=2.0, sats=3)
		#oints.points.append(time(hour=now.hour, minute=now.minute, second=now.second), lat=1.0, lon=2.0, sats=3)
		
		logging.info("   ===> Bencmark: put-data: points.put(%d)" % len(points.points.points))
		points.put()
		#for point in points:
		#	point.put()
		
		logging.info("   ===> Bencmark: put-data (%d)" % cnt)
		self.redirect("/benchmark")

class PurgeData(webapp.RequestHandler):
	def get(self):
		logging.info("   ===> Bencmark: purge-data")
		#logging.info("   ===> Bencmark: put-data")
		#debuguser = 353358019726996
		userdb = getuser()
		
		#cnt = int(self.request.get('cnt'))
		#cnt = 200
		
		#q = userdb.geos
		#db.delete(userdb.geos(keys_only=True).fetch(cnt))

		#db.delete(userdb.geos_pack.fetch(cnt))
		if self.request.get('all'):
			query = datamodel2.DBGPSPointP.all(keys_only=True).filter('user =', userdb).order('date').fetch(1000)
		else:
			query = datamodel2.DBGPSPointP.all(keys_only=True).filter('user =', userdb).filter('date <=', date.today()-timedelta(days=30)).order('date').fetch(1000)
		db.delete(query)
		logging.info("   ===> Bencmark: purge-data (%d)" % len(query))
		
		self.redirect("/benchmark")

class GetJson(webapp.RequestHandler):
	def get(self):
		gfrom = self.request.get('from')
		gto = self.request.get('to')
		logging.info("   ===> Bencmark: put-data %s-%s" % (gfrom, gto))

		userdb = getuser()
		datetimefrom = toUTC(datetime.strptime(gfrom, "%Y%m%d%H%M%S"))
		datetimeto = toUTC(datetime.strptime(gto, "%Y%m%d%H%M%S"))

		qdays = userdb.geos_pack.filter("date >=", datetimefrom.date()).filter("date <=", datetimeto.date()).fetch(10)

		days = []
		points = []

		for day in qdays:
			fulldate = toUTC(datetime(day.date.year, day.date.month, day.date.day))
			days.append(fulldate.strftime("%d/%m/%Y"))
			for k,point in day.points.points.items():
				fulldate = toUTC(datetime(day.date.year, day.date.month, day.date.day, k.hour, k.minute, k.second))
				#minimum info
				points.append(
					{
						#"d": fulldate.strftime("%d/%m/%Y %H:%M:%S"),
						"t": fulldate.strftime("%y%m%d%H%M%S"),
						"l": point['lat'],
						"o": point['lon'],
						"c": point['cource'],
						"s": point['speed'],
					}
				)

		self.response.headers['Content-Type']   = 'text/javascript; charset=utf-8'
		callback = self.request.get('callback')

		# compact

		jsonresp = {
			"responseData": {
				"answer": "ok",
				"from": gfrom,
				"to": gto,
				"from_date": "%s" % datetimefrom.date(),
				"to_date": "%s" % datetimeto.date(),
				"days_cnt": len(days),
				"days": days,
				"points_cnt": len(points),
				"points": points,
			}
		}

		#nejson = json.dumps(jsonresp, sort_keys=True, separators=(',',':'))
		nejson = json.dumps(jsonresp, separators=(',',':'))
		self.response.out.write(callback + "(" + nejson + ")\r")


class BenchmarkMulti(webapp.RequestHandler):
	def get(self):
		#userdb = getuser()

		cmd = self.request.get("cmd", "None")
		task = self.request.get("task", "None")
		cnt = int(self.request.get("cnt", "1"))

		if cmd == "put":
			pdate = date.today()

			dbv = datamodel2.DBmulti.get_by_key_name("multi_%d_%d_%d" % (pdate.year, pdate.month, pdate.day))
			if dbv is None:
			#points = datamodel2.DBGPSPointP(key_name="t_%d_%d_%d")
				dbv = datamodel2.DBmulti(key_name="multi_%d_%d_%d" % (pdate.year, pdate.month, pdate.day))
				dbv.date = pdate
				dbv.rvalue = ["0"]
			else:
				last = dbv.rvalue[-1]
				time.sleep(1)
				logging.info("   ===> BencmarkMulti: cnahge %s to %s" % (last, str(int(last)+1)))
				dbv.rvalue.append(str(int(last)+1))
			dbv.put()

			if task == "yes":
				self.response.out.write('<html><body>OK<br /><a href="/benchmark/multi">Back</a></body></html>')
				return
			self.redirect("/benchmark/multi")
			return
		elif cmd == "maketask":
			url = "/benchmark/multi?cmd=put&task=yes"
			for i in xrange(cnt):
				#countdown=i
				countdown=0
				taskqueue.add(url = url, method="GET", countdown=countdown)
			self.redirect("/benchmark/multi")
			return
		elif cmd == "purge":
			dbv = datamodel2.DBmulti.all(keys_only=True).fetch(500)
			db.delete(dbv)
			self.redirect("/benchmark/multi")
			return


		values = {}

		#pdate = date.today()
		dbv = datamodel2.DBmulti.all().fetch(100)
		values['dbv'] = dbv

		#values['pointscnt'] = datamodel.DBGPSPoint().all().filter('user =', userdb).count()
		#values['pointscnt'] = datamodel.DBGPSPoint2().all().filter('user =', userdb).count()
		#values['pointscnt'] = userdb.dbgpspoint2_set.count()
		#values['pointscnt'] = userdb.geos_pack.count()
		#points = 
		#values['points'] = userdb.geos_pack.order("-date").fetch(30)	# Последние 30 штук (месяц)
		path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.html')
		#self.response.headers['Content-Type']   = 'text/xml'
		self.response.out.write(template.render(path, values))


application = webapp.WSGIApplication(
	[
		('/benchmark/put-data.*', PutData),
		#('/benchmark/list-data.*', ListData),
		('/benchmark/purge-data.*', PurgeData),
		('/benchmark/get-json.*', GetJson),
		('/benchmark/multi.*', BenchmarkMulti),
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
