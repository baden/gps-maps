# -*- coding: utf-8 -*-
#import cgi
#from google.appengine.tools.dev_appserver import datastore
import logging
import os

from datetime import date
from datetime import datetime
from django.utils import simplejson as json
from google.appengine.api import users
from google.appengine.api import datastore
from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


class DBUser(db.Model):
	userid = db.IntegerProperty()			# Unique
	imei = db.StringProperty(multiline=False)	# IMEI
	phone = db.StringProperty(multiline=False)	# Phone number, for example: +380679332332
	password = db.StringProperty(multiline=False)	# User password
	date = db.DateTimeProperty(auto_now_add=True)	# Registration date
	desc = db.StringProperty(multiline=False)	# Описание

class GPSLogs(db.Model):
	user = db.ReferenceProperty(DBUser)
	text = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)

class Greeting(db.Model):
	author = db.UserProperty()
	content = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)

class DBGPSPoint(db.Model):
	user = db.ReferenceProperty(DBUser)
	cdate = db.DateTimeProperty(auto_now_add=True)
	date = db.DateTimeProperty()
	latitude = db.FloatProperty()
	longitude = db.FloatProperty()
	sats = db.IntegerProperty()
	fix = db.IntegerProperty()
	speed = db.FloatProperty()
	course = db.FloatProperty()
	altitude = db.FloatProperty()
	in1 = db.FloatProperty()		# Значение на аналоговом входе 1
	in2 = db.FloatProperty()		# Значение на агалоговом входе 2
	#power = db.FloatProperty()		# Уровень заряда батареи (на

class DBGPSBin(db.Model):
	user = db.ReferenceProperty(DBUser)
	cdate = db.DateTimeProperty(auto_now_add=True)
	dataid = db.IntegerProperty()
	data = db.BlobProperty()		# Пакет данных (размер ориентировочно до 64кбайт)

class DBGPSBinParts(db.Model):
	user = db.ReferenceProperty(DBUser)
	cdate = db.DateTimeProperty(auto_now_add=True)
	dataid = db.IntegerProperty()
	data = db.BlobProperty()		# Пакет данных (размер ориентировочно до 64кбайт)

class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()

		if user:
			#url = users.create_logout_url(self.request.uri)
			login_url = users.create_login_url(self.request.uri)
			username = user.nickname()
		else:
			self.response.out.write("<html><body>")
			self.response.out.write("Для работы с системой необходимо выполнить вход под своим Google-аккаунтом.<br>")
			self.response.out.write("Нажмите <a href=" + users.create_login_url(self.request.uri) + ">[ выполнить вход ]</a> для того чтобы перейти на сайт Google для ввода логина/пароля.<br>")
			self.response.out.write("После ввода логина/пароля вы будете возврыщены на сайт системы.")
			self.response.out.write("</body></html>")
			#self.redirect(users.create_login_url(self.request.uri))
			return

		allusers = DBUser.all().fetch(100)

		template_values = {
			'login_url': login_url,
			'username': username,
			'now': datetime.now(),
			'users': allusers,
		}

		#logging.warning("Test warning logging.");
		#logging.error("Test error logging.");
		#logging.debug("Test debug logging.");
		#logging.info("Test info logging.");
		#logging.critical("Test critical logging.");

		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))

class System(webapp.RequestHandler):
	def get(self):
		#self.response.headers['Content-Type'] = 'text/plain'	#minimizing data
		self.response.headers['Content-Type']   = 'text/javascript; charset=utf-8'
		callback = self.request.get('callback')
		jsonresp = {
			"responseData": {
				"answer": "ok",
			}
		}

		nejson = json.dumps(jsonresp)
		self.response.out.write(callback + "(" + nejson + ")\r")

class Guestbook(webapp.RequestHandler):
	def post(self):
		greeting = Greeting()

		if users.get_current_user():
			greeting.author = users.get_current_user()

		greeting.content = self.request.get('content')
		greeting.put()
		self.redirect('/')

def getUser(request):
	uimei = request.get('imei')
	ukey = request.get('ukey')
	uid = request.get('uid')
	if uid:
		userdb = DBUser().get_by_id(long(uid))
		#self.response.out.write('Get by id (%d)\r\n' % userid)

	if uimei:
		userdbq = DBUser().all().filter('imei =', uimei).fetch(1)
		#userdbq = DBUser().all().filter('imei =', uimei).get()
		if userdbq:
			userdb = userdbq[0] 
			#self.response.out.write('Get by imei (%s)\r\n' % uimei)
		else:
			userdb = None
			#self.response.out.write('User not found by imei (%s)\r\n' % uimei)
	return userdb

class AddLog(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'	#minimizing data
		userdb = getUser(self.request)

		#uimei = self.request.get('imei')
		#ukey = self.request.get('ukey')
		#uid = self.request.get('uid')
		text = self.request.get('text')

		#if uid:
		#    userdb = DBUser().get_by_id(long(uid))
		#    self.response.out.write('Get by id (%d)\r\n' % userid)

		#if uimei:
		#	userdbq = DBUser().all().filter('imei =', uimei).fetch(2)
		#	if userdbq:
		#		userdb = userdbq[0] 
		#		self.response.out.write('Get by imei (%s)\r\n' % uimei)
		#	else:
		#		userdb = None
		#		self.response.out.write('User not found by imei (%s)\r\n' % uimei)

		if userdb:
			gpslog = GPSLogs()
			gpslog.user = userdb
			gpslog.text = text
			gpslog.put()
			self.response.out.write('Add log for user (phone:%s IMEI:%s).\r\n' % (userdb.phone, userdb.imei))

		#userdb = DBUser().get('imei', user_imei)
		#userdb = DBUser().get_by_id(ids, parent)
		#self.response.out.write('OK.\r\n')
		#for ii in range(10):
		#    gpslog = GPSLogs()
		#    gpslog.userid = user_id
		#    gpslog.text = text
		#    gpslog.put()
		#    gpslog.put()
		#self.redirect('/')

		#response = Response()
		#self.response = response

		#self.response.out.write('Request body (%s)<br>'%self.request.body);
		#self.response.out.write('Request content_type (%s)<br>'%self.request.content_type)
		#self.response.out.write('Response header len (%s)<br>'%len(self.response.headers))
		#self.response.etag='my_etag'
		#self.response.out.write('Response content_type (%s)<br>'%self.response.etag)
		#self.response.out.write("aaa")
	#print "Hello, world!!!"
	#print self.response.headers
	#print aa
	#self.error(404)

	#header_data = self.response.hr_dataedata = "";
	def post(self):
		userid = int(self.request.get('id'))
		self.response.out.write('Request body (%s)<br>' % self.request.body)
		file = self.request.get('file')
		self.response.out.write('File: %s' % file)

class UsersList(webapp.RequestHandler):
	def get(self):
		dbusers_query = DBUser.all().order('-date')
		dbusers = dbusers_query.fetch(50)
		dbusers_count = dbusers_query.count()
		template_values = {
			'dbusers': dbusers,
			'users_count': dbusers_count,
		}
		path = os.path.join(os.path.dirname(__file__), 'users.html')
		self.response.out.write(template.render(path, template_values))

MAXLOGS = 20

class ViewLogs(webapp.RequestHandler):
	def get(self):
		#gpslogs_query = GPSLogs.all().order('-date').fetch(MAXLOGS+1)
		#gpslogs_query = db.GqlQuery("SELECT * FROM GPSLogs ORDER BY date DESC LIMIT 20")
		#gpslogs_query = db.GqlQuery("SELECT * FROM GPSLogs ORDER BY date DESC")
		#gpslogs_query = db.GqlQuery("SELECT * FROM GPSLogs ORDER BY date DESC OFFSET 1")
		#gpslogs_query = db.Query(GPSLogs)
		#gpslogs_query.offset(10)
		#gpslogs = gpslogs_query.fetch(20)
		#gpslogs = gpslogs_query.fetch(20)
		#gpslogs = gpslogs_query.get()

		datemark = self.request.get('date')
		prevmark = self.request.get('prev')
		#datemark = datetime(2009, 12, 23, 21, 0, 0)
		#datemark = datetime("2009-12-23 21:10:59.140000")
		#datemark = datetime.strptime(

		if prevmark:
			if prevmark == '0':
				urlprev = '<a class="Prev" href="logs">First</a>'
			else:
				urlprev = '<a class="Prev" href="logs?date=%s&prev=0">Prev</a>' % prevmark
		else:
			urlprev = ''

		if datemark:
			gpslogs = GPSLogs.all().filter('date <=', datetime.strptime(datemark, "%Y%m%d%H%M%S%f")).order('-date').fetch(MAXLOGS+1)
			#urlprev = '<a href="logs?date=%s">Prev</a> %s ' % (gpslogs[0].date.strftime("%d-%m-%y %H:%M:%S.%f"), datemark)  
		else:
			gpslogs = GPSLogs.all().order('-date').fetch(MAXLOGS+1)
		gpslogs_count = len(gpslogs)
		if gpslogs_count == MAXLOGS+1:
			if datemark:
				urlnext = '<a class="Next" href="logs?date=%s&prev=%s">Next</a> ' % (gpslogs[-1].date.strftime("%Y%m%d%H%M%S%f"), datemark)
			else:
				urlnext = '<a class="Next" href="logs?date=%s&prev=0">Next</a>' % gpslogs[-1].date.strftime("%Y%m%d%H%M%S%f")
			gpslogs.pop()
		else:
			urlnext = 'Next'

		#gpslogs = []
		#for gpslog in gpslogs_query:
			#gpslogs.append(gpslog)
		#slogs.extend(gpslogs_query.fetch(10))
		#gpslogs.extend(gpslogs_query.fetch(10))
		#gpslogs_count = gpslogs_query.count()
		#gpslogs_count = len(gpslogs)
		for gpslog in gpslogs:
			#gpslog.date = gpslog.date.replace(microsecond=0).replace(second=0)
			gpslog.sdate = gpslog.date.strftime("%d/%m/%Y %H:%M")
			try:
				uuser = gpslog.user
				gpslog.imei = uuser.imei 
			except:
				gpslog.imei = 'deleted' 
			#if not gpslog.user:
			#    gpslog.user.imei = "deleted"

		template_values = {
			'gpslogs': gpslogs,
			'urlnext': urlnext,
			'urlprev': urlprev,
		}
		path = os.path.join(os.path.dirname(__file__), 'logs.html')
		self.response.out.write(template.render(path, template_values))
		#try:
		#	self.response.out.write(template.render(path, template_values))
		#except:
		#	self.response.out.write("<html><body>Database error</body></html>")            
		#self.response.out.write(template.generate(path, template_values))
		#self.generate()


class DelLogs(webapp.RequestHandler):
	def get(self):
		logs = GPSLogs.all().order('date').fetch(100)
		for log in logs:
			log.delete()
		self.redirect("/logs")

class RegId(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'    #minimizing data
		imei = self.request.get('imei')
		phone = self.request.get('phone')
		passw = self.request.get('pass')
		self.response.out.write('imei=%s\r\nphone=%s\r\npass=%s\r\n' % (imei, phone, passw))

		#users = db.Query(DBUser).filter('phone', phone).fetch(2)
		users = db.Query(DBUser).filter('imei', imei).fetch(2)

		if users:
			newuser = users[0]
			self.response.out.write('User already in base.')
			if (newuser.phone != phone) | (newuser.password != passw):
				self.response.out.write(' Updating.\r\n')
				newuser.phone = phone
				newuser.password = passw
				newuser.put()
			else:
				self.response.out.write(' Ignoring.\r\n')
		else:
			newuser = DBUser()
			newuser.imei = imei
			newuser.phone = phone
			newuser.password = passw
			newuser.put()
			self.response.out.write('User added.\r\n')

		ukey = newuser.key()

		self.response.out.write('key=%s\r\n' % ukey)
		self.response.out.write('id=%s\r\n' % ukey.id())

class DelUser(webapp.RequestHandler):
	def get(self):
		ukey = self.request.get('key')
		uid = self.request.get('id')
		#duser = DBUser().get_by_key_name(cls, key_names, parent)
		if ukey:
			datastore.Delete(datastore.Key(ukey))

		if uid:
			userdb = DBUser().get_by_id(long(uid))
			userdb.delete()

		self.redirect("/users")
		#self.response.out.write('User deleted (key=%s).\r\n' % ukey)

class LastPos(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'    #minimizing data
		userdb = getUser(self.request)

		if userdb: 

			#imei = self.request.get('imei')
			latitude = float(self.request.get('latitude'))
			longitude = float(self.request.get('longitude'))
			sdatetime = self.request.get('datetime')
			sats = long(self.request.get('sats'))
			fix = long(self.request.get('fix'))
			speed = float(self.request.get('speed'))
			course = float(self.request.get('course'))
			altitude = float(self.request.get('alt'))
			in1 = float(self.request.get('in1'))*100.0/65535 
			in2 = float(self.request.get('in2'))*100.0/65535 

			if sdatetime:
				try:
					datestamp = datetime.strptime(sdatetime, "%d%m%y%H%M%S")
				except:
					datestamp = datetime.now()
			else:
				datestamp = datetime.now() 

			self.response.out.write('LastPos\r\n')
			#self.response.out.write('IMEI: %s\r\n' % userdb.imei)
			#self.response.out.write('User phone: %s\r\n' % userdb.phone)        
			#self.response.out.write('datetime: %s\r\n' % datestamp)
			#self.response.out.write('latitude: %.2f\r\n' % latitude)
			#self.response.out.write('longitude: %.2f\r\n' % longitude)
			#self.response.out.write('sats: %d\r\n' % sats)
			#self.response.out.write('fix: %d\r\n' % fix)
			#self.response.out.write('speed: %.2f\r\n' % speed)
			#self.response.out.write('course: %.2f\r\n' % course)
			#self.response.out.write('altitude: %.2f\r\n' % altitude)
			#self.response.out.write('in1: %.2f%%\r\n' % in1)
			#self.response.out.write('in2: %.2f%%\r\n' % in2)

			gpspoint = DBGPSPoint()
			gpspoint.user = userdb
			gpspoint.date = datestamp
			gpspoint.latitude = latitude
			gpspoint.longitude = longitude
			gpspoint.sats = sats
			gpspoint.fix = fix
			gpspoint.speed = speed
			gpspoint.course = course
			gpspoint.altitude = altitude
			gpspoint.in1 = in1
			gpspoint.in2 = in2
			gpspoint.put()
		else:
			self.response.out.write('User not found\r\n')

class Geos(webapp.RequestHandler):
	def get(self):
		geologs = DBGPSPoint.all().order('-date').fetch(MAXLOGS+1)
		#geologs = DBGPSPoint.all().order('-date').fetch(100)
		for geolog in geologs:
			try:
				uuser = geolog.user
				geolog.imei = uuser.imei 
			except:
				geolog.imei = 'deleted' 
			geolog.sdate = geolog.cdate.strftime("%d/%m/%Y %H:%M") 
		template_values = {
			'geologs': geologs,
		}
		path = os.path.join(os.path.dirname(__file__), 'geos.html')
		self.response.out.write(template.render(path, template_values))

class GeosJSON(webapp.RequestHandler):
	def get(self):
		start_time = datetime.now()
		logging.info("GeosJSON start (%s)" % start_time.strftime("%H:%M:%S"))

		userdb = getUser(self.request)

		if userdb:
			pass

		dif_time = datetime.now() - start_time
		logging.info("GeosJSON user ready (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))

		self.response.headers['Content-Type']   = 'text/javascript; charset=utf-8'

		callback = self.request.get('callback')

		datefrom_s = self.request.get('datefrom')
		if datefrom_s:
			datefrom = datetime.strptime(datefrom_s, "%d%m%Y%H%M%S")
		else:
			datefrom = datetime.now()

		logging.info("GeosJSON datefrom: %s" % datefrom)

		dateto_s = self.request.get('dateto')
		if dateto_s:
			dateto = datetime.strptime(dateto_s, "%d%m%Y%H%M%S")
		else:
			dateto = datetime.now()

		logging.info("GeosJSON dateto: %s" % dateto)

		first = self.request.get('first')
		if first:
			logging.info("GeosJSON first: %s" % first)
			if datefrom_s:
				geologs = DBGPSPoint.all().filter('user =', userdb).filter('date >=', datefrom).order('date').fetch(int(first))
			else:
				geologs = DBGPSPoint.all().filter('user =', userdb).order('date').fetch(int(first))
				pass
		else:
			last = self.request.get('last')
			if last:
				logging.info("GeosJSON last: %s" % last)
				geologs = DBGPSPoint.all().filter('user =', userdb).filter('date <=', dateto).order('-date').fetch(int(last))
			else:
				geologs = DBGPSPoint.all().filter('user =', userdb).filter('date >=', datefrom).filter('date <=', dateto).order('-date').fetch(300)

		#self.response.out.write("// User imei: %s\r// Date from: %s\r// Date to: %s\r" % (userdb.imei, datefrom, dateto))

#.filter('date <=', datetime.strptime(datemark, "%Y%m%d%H%M%S%f"))
		#geologs = DBGPSPoint.all().order('-date').filter('user =', userdb)
		#geologs = DBGPSPoint.all().order('-date').fetch(500)
		#geologs = DBGPSPoint.all().order('-date').fetch(MAXLOGS+1)

		dif_time = datetime.now() - start_time
		logging.info("GeosJSON db ready (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))

		results = []

		for geolog in geologs:
			result = {
				"date": geolog.date.strftime("%d/%m/%Y %H:%M:%S"),
				"day": geolog.date.strftime("%m/%d/%Y %H:%M"),
				"lat": geolog.latitude,
				"long": geolog.longitude,
				"sats": geolog.sats,
				"fix": geolog.fix,
				"speed": geolog.speed,
				"course": geolog.course,
				"alt": geolog.altitude,
				"in1": geolog.in1,
				"in2": geolog.in2,
				}
			#try:
			#	uuser = geolog.user
			#	geolog.imei = uuser.imei
			#	result["imei"] = uuser.imei
			#except:
			#	geolog.imei = 'deleted' 
			#	result["imei"] = "none"

			results.append(result)

			#user = db.ReferenceProperty(DBUser)
			#cdate = db.DateTimeProperty(auto_now_add=True)
			#geolog.sdate = geolog.cdate.strftime("%d/%m/%Y %H:%M") 

		if geologs:
			if first:
				jsonresp = {
					"responseData": {
						"results": results, 
						"config": 0,
						"dateminjs": geologs[0].date.strftime("%m/%d/%Y %H:%M"),
						"datemaxjs": geologs[-1].date.strftime("%m/%d/%Y %H:%M"),
						"datemin": geologs[0].date.strftime("%d/%m/%Y %H:%M:%S"),
						"datemax": geologs[-1].date.strftime("%d/%m/%Y %H:%M:%S"),
					}
				}
			else:
				jsonresp = {
					"responseData": {
						"results": results, 
						"config": 0,
						"dateminjs": geologs[-1].date.strftime("%m/%d/%Y %H:%M"),
						"datemaxjs": geologs[0].date.strftime("%m/%d/%Y %H:%M"),
						"datemin": geologs[-1].date.strftime("%d/%m/%Y %H:%M:%S"),
						"datemax": geologs[0].date.strftime("%d/%m/%Y %H:%M:%S"),
					}
				}
		else:
			jsonresp = {
				"responseData": {
					"results": results, 
					"config": 0,
				}
			}


		dif_time = datetime.now() - start_time
		logging.info("GeosJSON response ready (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))


		nejson = json.dumps(jsonresp)
		self.response.out.write(callback + "(" + nejson + ")\r")

		dif_time = datetime.now() - start_time
		logging.info("GeosJSON json-out ready (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))

		logging.info("GeosJSON data: %d values" % len(results))

		return

		self.response.out.write("// Old version:\r")
		jsondata = callback + "("
		jsondata += """
		{
				"responseData": {
					"results":[
					{
						"GsearchResultClass":"GwebSearch",
						"unescapedUrl":"http://www.google.com/",
						"url":"http://www.google.com/",
						"visibleUrl":"www.google.com",
						"cacheUrl":"http://www.google.com/search?q\u003dcache:zhool8dxBV4J:www.google.com",
						"title":"\u003cb\u003eGoogle\u003c/b\u003e",
						"titleNoFormatting":"Google",
						"content":"Enables users to search the Web, Usenet, and images. Features include PageRank,   caching and translation of results, and an option to find similar pages."
					},{
						"GsearchResultClass":"GwebSearch",
						"unescapedUrl":"http://maps.google.com/",
						"url":"http://maps.google.com/",
						"visibleUrl":"maps.google.com",
						"cacheUrl":"http://www.google.com/search?q\u003dcache:dkf5u2twBXIJ:maps.google.com",
						"title":"\u003cb\u003eGoogle\u003c/b\u003e Maps",
						"titleNoFormatting":"Google Maps",
						"content":"Find local businesses, view maps and get driving directions in \u003cb\u003eGoogle\u003c/b\u003e Maps."
					},{
						"GsearchResultClass":"GwebSearch",
						"unescapedUrl":"http://video.google.com/",
						"url":"http://video.google.com/",
						"visibleUrl":"video.google.com",
						"cacheUrl":"http://www.google.com/search?q\u003dcache:yzZ7MosNOvsJ:video.google.com",
						"title":"\u003cb\u003eGoogle\u003c/b\u003e Videos",
						"titleNoFormatting":"Google Videos",
						"content":"Search and watch millions of videos. Includes forum and personalized   recommendations."
					},{
						"GsearchResultClass":"GwebSearch",
						"unescapedUrl":"http://www.google.org/",
						"url":"http://www.google.org/",
						"visibleUrl":"www.google.org",
						"cacheUrl":"http://www.google.com/search?q\u003dcache:AkOXzKdBYp4J:www.google.org",
						"title":"\u003cb\u003eGoogle\u003c/b\u003e.org",
						"titleNoFormatting":"Google.org",
						"content":"The philanthropic arm of the company. Lists its activities."
					}],
					"cursor":{
						"pages":[
							{
								"start":"0",
								"label":1
							},{
								"start":"4",
								"label":2
							},{
								"start":"8",
								"label":3
							},{
								"start":"12",
								"label":4
							},{
								"start":"16",
								"label":5
							},{
								"start":"20",
								"label":6
							},{
								"start":"24",
								"label":7
							},{
								"start":"28",
								"label":8
							}
						],
						"estimatedResultCount":"166000000",
						"currentPageIndex":0,
						"moreResultsUrl":"http://www.google.com/search?oe\u003dutf8\u0026ie\u003dutf8\u0026source\u003duds\u0026start\u003d0\u0026hl\u003dru\u0026q\u003dgoogle"
					}
				},
				"responseDetails": null,
				"responseStatus": 200
			}
		"""
		jsondata += ")"
		self.response.out.write(jsondata)
		pass

class DelGeos(webapp.RequestHandler):
	def get(self):
		geologs = DBGPSPoint.all().order('-date').fetch(500)
		if geologs:
			db.delete(geologs)
		#for geolog in geologs:
		#	geolog.delete()
		self.redirect("/geos")

class CSSfiles(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type']   = 'text/css'
		self.response.headers['Cache-Control']  = 'public, max-age=315360000'

		#self.response.out.write('file: %s\r\n' % __file__)
		#self.response.out.write('url: %s\r\n' % self.request.url)
		#self.response.out.write('url path: %s\r\n' % self.request.path)
		path = os.path.join(os.path.dirname(__file__), '.'+self.request.path)
		#self.response.out.write('dir = %s\r\n' % os.path.dirname(__file__))
		#self.response.out.write('path = %s\r\n' % path)
		try:
			css_stream = open(path, 'r')
			self.response.out.write(css_stream.read())  
		except IOError, e:
			self.response.out.write('/* cannot open file %s */' % path)  
		pass

conf_parms = [
	{
		'name':'gps_V0', 'param': 'gps.V0',
		'title': 'Минимальная фиксируемая скорость', 'units': 'км/ч',
		'values': [10, 20, 10, 20],
		'recomends': '5...20',
		'range': '1...60',
		'help': 'При скорости движения менее установленной\nсчитается что объект неподвижен.'
	}, {
		'name':'gps_T0', 'param': 'gps.T0',
		'title': 'Время остановки для фиксации значения', 'units': 'сек',
		'values': [10, 10, 10, 10],
		'recomends': '5...60',
		'range': '5...120',
	}, {
		'name':'gps_T1', 'param': 'gps.T1',
		'title': 'Периодичность записи координат', 'units': 'сек',
		'values': [10, 600, 10, 600],
		'recomends': '5...20',
		'range': '1...6000',
	}, {
		'name':'gps_T2', 'param': 'gps.T2',
		'title': 'Периодичность отправки координат при движении объекта', 'units': 'мин',
		'values': [1, 60, 1, 120],
		'recomends': '1...240',
		'range': '1...240',
	}, {
		'name':'gps_T3', 'param': 'gps.T3',
		'title': 'Периодичность отправки координат при стоянке объекта', 'units': 'мин',
		'values': [10, 120, 10, 240],
		'recomends': '5...240',
		'range': '1...240',
	}, {
		'name':'gps_T4', 'param': 'gps.T4',
		'title': 'Время, через которое GPS-приемник обесточивается после остановки объекта', 'units': 'час',
		'values': [12, 4, 12, 2],
		'recomends': '1...24',
		'range': '0...24',
	}, {
		'name':'gps_T5', 'param': 'gps.T5',
		'title': 'Периодичность отправки последних координат в спящем режиме', 'units': 'час',
		'values': [1, 2, 1, 4],
		'recomends': '1...24',
		'range': '1...24',
	}, {
		'name':'gps_S1', 'param': 'gps.S1',
		'title': 'Минимальная фиксируемая дистанция', 'units': 'метры',
		'values': [100, 1000, 100, 1000],
		'recomends': '100...2000',
		'range': '100...10000',
	}, {
		'name':'gps_A1', 'param': 'gps.A1',
		'title': 'Минимальный фиксируемый угол направления движения', 'units': 'градусы',
		'values': [5, 10, 5, 15],
		'recomends': '5...15',
		'range': '1...45',
	}, {
		'name':'gps_B1', 'param': 'gps.B1',
		'title': 'Объем памяти, по заполнению которого производится принудительная отправка', 'units': 'КБайты',
		'values': [512, 512, 512, 512],
		'recomends': '5...512',
		'range': '1...512',
	},
]

class Config(webapp.RequestHandler):
	def get(self):
		allusers = DBUser.all().fetch(100)
		template_values = {
			'now': datetime.now(),
			'configs': conf_parms,
			'users': allusers,
		}
		path = os.path.join(os.path.dirname(__file__), 'config.html')
		self.response.out.write(template.render(path, template_values))

class Help(webapp.RequestHandler):
	def get(self):
		self.response.out.write("<html><body>Sorry, no help yet. Comming soon...<br><a href=\"/\">To main page</a></body></html>")
		pass

class TestBin(webapp.RequestHandler):
	def get(self):
		logging.debug("TEST_BIN_GET")
		#self.response.headers['Content-Type'] = 'application/octet-stream'
		#bdata = ''
		#bdata += 'AB'
		#self.response.out.write(bdata)
		#request.
		self.response.out.write("<html><body>")

		#url = "http://www.google.com/"
		#result = urlfetch.fetch(url)
		#if result.status_code == 200:
		#    self.response.out.write(result.content)
		surl = self.request.url
		sheaders = {'Content-Type': 'application/octet-stream'}
		sdata = 'ABCDEFG'

		if surl.startswith('http://localhost'):
		#if url.startswith('http://loc'):
			self.response.out.write('[local]<br>')
		else:
			self.response.out.write('[online]<br>')

		surl = "http://localhost/bingeos"
		surl = "http://localhost/"
		#surl = "http://www.google.com/"
		result = urlfetch.fetch(
			url = surl,
			method = urlfetch.GET,
			headers = sheaders,
			payload = sdata
		)
		#result = urlfetch.fetch(url)
		if result.status_code == 200:
			self.response.out.write('COMPLETED<br>')
		else:
			self.response.out.write('ERROR [%d]<br>' % result.status_code)

		self.response.out.write("name = %s<br>" % self.request.url)
		self.response.out.write("Sorry, no help yet. Comming soon...<br><a href=\"/\">To main page</a>")
		self.response.out.write("</body></html>")

	def post(self):
		logging.debug("TEST_BIN_POST")
		#self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('OK\r\n')

class BinGeos(webapp.RequestHandler):
	def get(self):
		logging.info("$=$ TEST_BIN_GET")
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('OK\r\n')

	def post(self):
		_log = "TEST_BIN_POST ["

		#logging.info("$=$ TEST_BIN_POST")

		self.response.headers['Content-Type'] = 'text/plain'

		sdataid = self.request.get('dataid')
		if sdataid:
			dataid = int(sdataid, 16)
		else:
			self.response.out.write('ANSWER: NODATAID\r\n')
			return

		userdb = getUser(self.request)

		if not userdb:
			uimei = self.request.get('imei')
			#ukey = request.get('ukey')
			#uid = request.get('uid')

			userdb = DBUser()
			userdb.imei = uimei
			userdb.phone = ""
			userdb.password = ""
			userdb.desc = u"Новая система. Нет описания."
			userdb.put()
			#self.response.out.write('User added.\r\n')

		pdata = self.request.body

		_log += '\nData ID: %d' % dataid

		dataenc = self.request.get('enc')
		if dataenc:
			if dataenc == 'utf8':
				bdata = pdata.decode('utf8')
				pdata = ""
				for data in bdata:
					pdata += chr(ord(data))
				logging.info('type = ')
				logging.info(type(pdata))
				logging.info(type(self.request.body))
				#pdata = pdata.decode('utf8').encode('koi-8')
				#pdata = str(pdata)
				
				pass
		
		_log += '\nData size: %d' % len(pdata)
		#_log += '\nData (HEX):'
		#for data in pdata:
		#	_log += ' %02X' % ord(data)

		if userdb:
			#self.response.out.write('headers: %s\r\n' % self.request.headers)
			#self.response.out.write('imei: %s\r\n' % userdb.imei)
			#self.response.out.write('phone: %s\r\n' % userdb.phone)
			#self.response.out.write('datasize: %d\r\n' % len(pdata))

			#	user = db.ReferenceProperty(DBUser)
			#	cdate = db.DateTimeProperty(auto_now_add=True)
			#	dataid = db.IntegerProperty()
			#	#data = db.BlobProperty()		# Пакет данных (размер ориентировочно до 64кбайт)
			#	data = db.TextProperty()		# Пакет данных (размер ориентировочно до 64кбайт)
			newbin = DBGPSBin()
			newbin.user = userdb
			newbin.dataid = dataid
			newbin.data = pdata #db.Text(pdata)
			newbin.put()

			_log += '\nSaved to DBGPSBin creating tasque'

			url = "/parsebingeos?dataid=%s&key=%s" % (dataid, newbin.key())
			#taskqueue.add(url = url % self.key().id(), method="GET", countdown=countdown)
			countdown=0
			taskqueue.add(url = url, method="GET", countdown=countdown)

			self.response.out.write('ANSWER: OK\r\n')
		else:
			self.response.out.write('ANSWER: USER_NOT_FOUND\r\n')

		#_log += "\n {DATABASE PUT() DISABLED}"
		logging.info(_log)

def SaveGPSPointFromBin(pdata, result):
	#logging.info('[%d]' % len(pdata))
	#_log += '*'

	#_log += '\nLastPos:'
	#_log += '\n IMEI: %s\r\n' % result.user.imei

	day = ord(pdata[0])
	month = ord(pdata[1]) & 0x0F
	year = (ord(pdata[1]) & 0xF0)/16 + 2010
	hours = ord(pdata[2])
	minutes = ord(pdata[3])
	seconds = ord(pdata[4])
	datestamp = datetime(year, month, day, hours, minutes, seconds)

	latitude = float(ord(pdata[5])) + (float(ord(pdata[6])) + float(ord(pdata[7])*100 + ord(pdata[8]))/10000.0)/60.0
	longitude = float(ord(pdata[9])) + (float(ord(pdata[10])) + float(ord(pdata[11])*100 + ord(pdata[12]))/10000.0)/60.0
	if ord(pdata[13]) & 1:
		latitude = - latitude
	if ord(pdata[13]) & 2:
		longitude = - longitude

	sats = ord(pdata[14])

	fix = 1
	speed = float(ord(pdata[15])) + float(ord(pdata[16])) / 100.0;
	course = float(ord(pdata[17])) + float(ord(pdata[18])) / 100.0;
	altitude = 100.0 * float(ord(pdata[19]) + ord(pdata[20])) / 10.0;

	if(ord(pdata[21])) != 255:	#CRC
		#_log += '{CRC_ERROR}skiped'
		return

	if(ord(pdata[22])) != 255:	#CRC
		#_log += '{CRC_ERROR}skiped'
		return

	#in1 = float(self.request.get('in1'))*100.0/65535 
	#in2 = float(self.request.get('in2'))*100.0/65535 
	in1 = 0.0
	in2 = 0.0

	#_log += '\n Date: %s' % datestamp.strftime("%d/%m/%Y %H:%M:%S")
	#_log += '\n Latitude: %.5f' % latitude
	#_log += '\n Longitude: %.5f' % longitude
	#_log += '\n Satelits: %d' % sats
	#_log += '\n Speed: %.5f' % speed
	#_log += '\n Course: %.5f' % course
	#_log += '\n Altitude: %.5f' % altitude
	#logging.info('[%s]' % datestamp.strftime("%d/%m/%Y %H:%M:%S"))

	gpspoint = DBGPSPoint()
	gpspoint.user = result.user
	gpspoint.date = datestamp
	gpspoint.latitude = latitude
	gpspoint.longitude = longitude
	gpspoint.sats = sats
	gpspoint.fix = fix
	gpspoint.speed = speed
	gpspoint.course = course
	gpspoint.altitude = altitude
	gpspoint.in1 = in1
	gpspoint.in2 = in2
	return gpspoint
	#gpspoint.put()

class ParseBinGeos(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('PARSE\r\n')

		_log = "PARSE_BIN_GEOS{_GET} ["

		#query = DBGPSBin().all()
		#result = query.get()
		key = db.Key(self.request.get('key'))
		#result = DBGPSBin().all().get(key)
		result = db.get(key)
		if result:
		#for result in results:
			dataid = result.dataid
			pdata = result.data
			_log += '\nDATA ID: %d' % dataid
			_log += '\nDATA LENGHT: %d' % len(pdata)

			if len(pdata) > (24*450):	# было 24*60 (1 минута на самой высокой скорости)
				_log += '\nSPLIT BINDATA BY 10800 bytes (450 points):'
				while len(pdata) > 0:
					newbin = DBGPSBin()
					newbin.user = result.user
					newbin.dataid = result.dataid
					newbin.data = pdata[:(24*450)]
					newbin.put()

					_log += '\nSaved to DBGPSBin creating tasque'

					url = "/parsebingeos?dataid=%d&key=%s" % (dataid, newbin.key())
					#taskqueue.add(url = url % self.key().id(), method="GET", countdown=countdown)
					countdown=0
					taskqueue.add(url = url, method="GET", countdown=countdown)

					pdata = pdata[(24*450):]

				self.response.out.write('SPLIT TASK\r\n')
				result.delete()
				_log += '\nOriginal data deleted.'
				logging.info(_log)
				return


			#_log += '\nData (HEX):'
			#for data in pdata:
			#	_log += ' %02X' % ord(data)

			_log += '\nParsing...'

			_log += 'spliting...'
			parts = pdata.split('\xF2')
			_log += '%d patrs...' % len(parts)

			odata_s = None
			odata_f = None
			if len(parts[0]) < 23:
				_log += 'pat[0](%d) is cutted - its ok...' % len(parts[0])
				if len(parts[0]) != 0:
					odata_s = parts[0]
				del parts[0]

			if len(parts) > 0:
				if len(parts[-1]) != 23:
					_log += 'pat[-1] is cutted - its ok...'
					odata_f = parts[-1]
					del parts[-1]

			_log += '%d patrs now...' % len(parts)

			position = 0
			points = []
			for part in parts:
				if len(part) == 23:
					_log += '*'
					points.append(SaveGPSPointFromBin(part, result))
				else:
					_log += '\npat%d is corrupted' % position
				position = position+1

			#position = 0
			#for data in pdata:
			#	code = ord(data)
			#	if code == 0x20:
			#		_log += 'cathed at position %d' % position
			#	position = position+1
			_log += '\nPurge future (break) cut-part...'
			futparts = DBGPSBinParts().all().filter('user =', result.user).filter('dataid >=', result.dataid).fetch(10)
			for futpart in futparts:
				_log += '*'
				futpart.delete()

			if odata_s:
				_log += '\nFinding prevoiuse cut-part...'
				prevpart = DBGPSBinParts().all().filter('user =', result.user).filter('dataid =', result.dataid-1).get()
				if prevpart:
					_log += 'ok. mergin...'
					part = prevpart.data + odata_s
					if len(part) == 23:
						_log += 'ok.'
						points.append(SaveGPSPointFromBin(part, result))
					else:
						_log += 'fail [%d]:' % len(part)
						for data in part:
							_log += ' %02X' % ord(data)
					prevpart.delete()
				else:
					_log += 'fail.'
			#geologs = DBGPSPoint.all().filter('user =', userdb).filter('date >=', datefrom).filter('date <=', dateto).order('-date').fetch(300)
			#	part1 = DBGPSBinParts()
			#	part1.user = result.user
			#	part1.dataid = result.dataid
			#	part1.data = odata_s
			#	part1.start = False
			#	part1.put()
			if odata_f:
				part2 = DBGPSBinParts()
				part2.user = result.user
				part2.dataid = result.dataid
				part2.data = odata_f
				_log += '\nSaving cutting part.'
				part2.put()

			db.put(points)		# Сохраним GPS-точки
			result.delete()
			self.response.out.write('OK\r\n')
			_log += '\nData deleted.'
			
			#for name in os.environ.keys():
			#	self.response.out.write("%s = %s\n" % (name, os.environ[name]))
		else:
			self.response.out.write('OK NODATA\r\n')
		
		logging.info(_log)

__hide2comment = """
			_log += '\nGPS DATA:'

			day = ord(pdata[0])
			month = ord(pdata[1]) & 0x0F
			year = (ord(pdata[1]) & 0xF0)/16 + 2010
			hours = ord(pdata[2])
			minutes = ord(pdata[3])
			seconds = ord(pdata[4])

			datestamp = datetime(year, month, day, hours, minutes, seconds)

			latitude = float(ord(pdata[6])) + (float(ord(pdata[7])) + float(ord(pdata[8]) + ord(pdata[9])*256)/10000.0)/60.0
			longitude = float(ord(pdata[10])) + (float(ord(pdata[11])) + float(ord(pdata[12]) + ord(pdata[13])*256)/10000.0)/60.0

			if ord(pdata[5]) & 1:
				latitude = - latitude
			if ord(pdata[5]) & 2:
				longitude = - longitude

			sats = ord(pdata[14])
			fix = 1
			speed = float(ord(pdata[15])) + float(ord(pdata[16])) / 100.0;
			course = float(ord(pdata[17])) + float(ord(pdata[18])) / 100.0;
			altitude = float(ord(pdata[20]) + 256*ord(pdata[21])) / 10.0;

			#in1 = float(self.request.get('in1'))*100.0/65535 
			#in2 = float(self.request.get('in2'))*100.0/65535 
			in1 = 0.0
			in2 = 0.0


			_log += '\n Date: %s' % datestamp.strftime("%d/%m/%Y %H:%M:%S")
			_log += '\n Latitude: %.5f' % latitude
			_log += '\n Longitude: %.5f' % longitude
			_log += '\n Satelits: %d' % sats
			_log += '\n Speed: %.5f' % speed
			_log += '\n Course: %.5f' % course
			_log += '\n Altitude: %.5f' % altitude
			#self.response.out.write('data: %s\r\n' % pdata)


			#self.response.out.write('LastPos\r\n')
			#self.response.out.write('IMEI: %s\r\n' % userdb.imei)
			#self.response.out.write('User phone: %s\r\n' % userdb.phone)        
			#self.response.out.write('datetime: %s\r\n' % datestamp)
			#self.response.out.write('latitude: %.2f\r\n' % latitude)
			#self.response.out.write('longitude: %.2f\r\n' % longitude)
			#self.response.out.write('sats: %d\r\n' % sats)
			#self.response.out.write('fix: %d\r\n' % fix)
			#self.response.out.write('speed: %.2f\r\n' % speed)
			#self.response.out.write('course: %.2f\r\n' % course)
			#self.response.out.write('altitude: %.2f\r\n' % altitude)
			#self.response.out.write('in1: %.2f%%\r\n' % in1)
			#self.response.out.write('in2: %.2f%%\r\n' % in2)

			gpspoint = DBGPSPoint()
			gpspoint.user = userdb
			gpspoint.date = datestamp
			gpspoint.latitude = latitude
			gpspoint.longitude = longitude
			gpspoint.sats = sats
			gpspoint.fix = fix
			gpspoint.speed = speed
			gpspoint.course = course
			gpspoint.altitude = altitude
			gpspoint.in1 = in1
			gpspoint.in2 = in2

			#gpspoint.put()
"""

class GetBinGeos(webapp.RequestHandler):
	def get(self):
		result = db.get(db.Key(self.request.get('key')))
		if result:
			body = result.data
			self.response.headers['Content-Type'] = 'application/octet-stream'
			self.response.headers['Content-Length'] = "%d" % len(body)
			self.response.out.write(body)
		else:
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.out.write('NODATA\r\n')

class Map(webapp.RequestHandler):
	def get(self):
		allusers = DBUser.all().fetch(100)
		template_values = {
			'users': allusers,
			'now': datetime.now(),
		}
		path = os.path.join(os.path.dirname(__file__), 'map.html')
		self.response.out.write(template.render(path, template_values))

class RawData(webapp.RequestHandler):
	def get(self):
		print "RAW DATA"
		logging.info("DO RAW DATA")


class DBGPSPoint2(db.Model):
	user = db.ReferenceProperty(DBUser, name='a')
	cdate = db.DateTimeProperty(auto_now_add=True, name='b')
	date = db.DateTimeProperty(name='c')
	latitude = db.FloatProperty(name='d')
	longitude = db.FloatProperty(name='e')
	sats = db.IntegerProperty(name='f')
	fix = db.IntegerProperty(name='g')
	speed = db.FloatProperty(name='h')
	course = db.FloatProperty(name='i')
	altitude = db.FloatProperty(name='j')
	in1 = db.FloatProperty(name='k')		# Значение на аналоговом входе 1
	in2 = db.FloatProperty(name='l')		# Значение на агалоговом входе 2
	#power = db.FloatProperty()		# Уровень заряда батареи (на

class Profiler():
	def __init__(self, logging):
		"""
		@param encoder: Encoder containing the stream.
		@type encoder: L{amf3.Encoder<pyamf.amf3.Encoder>}
		"""
		self.start_time = datetime.now()
		self.logging = logging
		self.logging.info("Profile start (%s)\n" % self.start_time.strftime("%H:%M:%S"))

	def tick(self):
		dif_time = datetime.now() - self.start_time
		self.logging.info("Profile (+%.4fsec)\n" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))

	def time(self):
		dif_time = datetime.now() - self.start_time
		return dif_time.seconds + float(dif_time.microseconds)/1000000.0
		
class TestDB(webapp.RequestHandler):
	def create(self):
		trect = DBGPSPoint2()
		trect.date = datetime.now()
		trect.latitude = 1.0
		trect.longitude = 1.0
		trect.sats = 1
		trect.fix = 1
		trect.speed = 1.0
		trect.course = 1.0
		trect.altitude = 1.0
		trect.in1 = 1.0
		trect.in2 = 1.0
		trect.put()

	def prepare(self):
		trect = DBGPSPoint2()
		trect.date = datetime.now()
		trect.latitude = 1.0
		trect.longitude = 1.0
		trect.sats = 1
		trect.fix = 1
		trect.speed = 1.0
		trect.course = 1.0
		trect.altitude = 1.0
		trect.in1 = 1.0
		trect.in2 = 1.0
		return trect

	def get(self):
		profiler = Profiler(logging)

		cmd = self.request.get('cmd')
		cnt = self.request.get('cnt')
		batch = self.request.get('batch')
		values = {
			'now': datetime.now(),
		}

		answer = ''

		if not cmd:
			values['answer'] = 'NONE'
			#self.response.headers['Content-Type'] = 'text/plain'
			#self.response.out.write('NODATA\r\n')
		else:
			if cmd[:6] == "create":
				answer = 'создания'
				if batch:
					trects = []
					for i in xrange(int(batch)):
						trects.append(self.prepare())
					db.put(trects)
				elif cnt:
					for i in xrange(int(cnt)):
						self.create()
				else:
					self.create()
			elif cmd[:6] == "delete":
				answer = 'удаления'
				#if not cnt:
				#	cnt = '1'
				if cnt:
					results = DBGPSPoint2().all().fetch(int(cnt))
					for result in results:
						result.delete()
				elif batch:
					results = DBGPSPoint2().all().fetch(int(batch))
					if results:
						db.delete(results)
				else:
					results = DBGPSPoint2().all().fetch(1)
					if results:
						results[0].delete()

		values['runtime'] = profiler.time() * 1000
		values['answer'] = answer
		path = os.path.join(os.path.dirname(__file__), 'testdb.html')
		self.response.out.write(template.render(path, values))
		#self.redirect('testdb.html')

#class myWSGIApplication(webapp.WSGIApplication):
#	def __call__(self, environ, start_response):
#		webapp.WSGIApplication.__call__(self, environ, my_start_response)
#		return ['']

#application = myWSGIApplication(
application = webapp.WSGIApplication(
	[('/', MainPage),
	('/regid', RegId),
	('/sign', Guestbook),
	('/addlog', AddLog),
	('/users.*', UsersList),
	('/delUser.*', DelUser),
	('/logs.*', ViewLogs),
	('/dellogs.*', DelLogs),
	('/delgeos.*', DelGeos),
	('/lastpos.*', LastPos),
	('/geosjson', GeosJSON),
	('/geos.*', Geos),
	('/stylesheets.*', CSSfiles),
	('/config.*', Config),
	('/help.*', Help),
	('/testbin.*', TestBin),
	('/bingeos.*', BinGeos),
	('/parsebingeos.*', ParseBinGeos),
	('/getbin.*', GetBinGeos),
	('/map.*', Map),
	('/raw', RawData),
	('/testdb.*', TestDB),
	('/system.*', System),
	],
	debug=True
)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
