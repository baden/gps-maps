# -*- coding: utf-8 -*-
#import cgi
#from google.appengine.tools.dev_appserver import datastore
import logging
import os
import zlib
import math
import random

#from datetime import date
#from datetime import datetime
from datetime import date, timedelta, datetime

from django.utils import simplejson as json
from google.appengine.api import users
from google.appengine.api import datastore
from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
#from google.appengine.tools import bulkloader

# Must set this env var *before* importing any part of Django.
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#TIME_ZONE = 'America/Los_Angeles'  # i.e., Mountain View

from google.appengine.ext.webapp import template
from google.appengine.api import memcache



#import models
import datamodel
import utils

#ADMIN_USERNAME = 'baden.i.ua'

SERVER_NAME = os.environ['SERVER_NAME']
MAX_TRACK_FETCH	= 500

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

#utc = UTC()

#import pytz

def checkUser(uri, response):
	user = users.get_current_user()

	if user:
		#url = users.create_logout_url(self.request.uri)
		login_url = users.create_login_url(uri)
		username = user.nickname()
	else:
		#response.out.write("<html><body>")
		#response.out.write("Для работы с системой необходимо выполнить вход под своим Google-аккаунтом.<br>")
		#response.out.write("Нажмите <a href=" + users.create_login_url(uri) + ">[ выполнить вход ]</a> для того чтобы перейти на сайт Google для ввода логина/пароля.<br>")
		#response.out.write("После ввода логина/пароля вы будете возврыщены на сайт системы.")
		#response.out.write("</body></html>")
		self.redirect(users.create_login_url(self.request.uri))
		return False
	return {
		'login_url': login_url,
		'username': username,
		#'admin': username == ADMIN_USERNAME,
		'admin': users.is_current_user_admin(),
	}

class TemplatedPage(webapp.RequestHandler):
	def __init__(self):
		#self.uimei = self.request.get('imei')
		#logging.info(" TemplatedPage-init")
		self.user = users.get_current_user()

		accounts = datamodel.DBAccounts().all().filter('user =', self.user).fetch(1)
		#key_name = "FWBOOT%04X"

		if accounts:
			self.account = accounts[0]
		else:
			self.account = datamodel.DBAccounts(key_name = "acc_%s" % self.user.user_id())
			self.account.user = self.user
			self.account.name = u"Имя не задано"
			self.account.systems = []
			self.account.put()

		self.users = []
		for account in self.account.systems:
			self.users.append(db.get(db.Key(account)))

		if len(self.users) == 1:
			self.single = True
		else:
			self.single = False

	def write_template(self, values, alturl=None):
		if self.user:
			#url = users.create_logout_url(self.request.uri)
			login_url = users.create_login_url(self.request.uri)
			values['login_url'] = login_url
			values['username'] = self.user.nickname()
			values['admin'] = users.is_current_user_admin()
			values['server_name'] = SERVER_NAME
			values['account'] = self.account
			values['single'] = self.single
			values['users'] = self.users
			#if 'imei' not in values: values['imei'] = self.uimei

			if alturl:
				path = os.path.join(os.path.dirname(__file__), 'templates', alturl)
			else:
				path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.html')
			#self.response.headers['Content-Type']   = 'text/xml'
			self.response.out.write(template.render(path, values))
		else:
			#self.response.out.write("<html><body>")
			#self.response.out.write("Для работы с системой необходимо выполнить вход под своим Google-аккаунтом.<br>")
			#self.response.out.write("Нажмите <a href=" + users.create_login_url(self.request.uri) + ">[ выполнить вход ]</a> для того чтобы перейти на сайт Google для ввода логина/пароля.<br>")
			#self.response.out.write("После ввода логина/пароля вы будете возврыщены на сайт системы.")
			#self.response.out.write("</body></html>")
			self.redirect(users.create_login_url(self.request.uri))


class TemplatedPage2(webapp.RequestHandler):
	def __init__(self):
		#self.uimei = self.request.get('imei')
		#logging.info(" TemplatedPage-init")
		self.user = users.get_current_user()

		self._account = None

		"""
		self.users = []
		for account in self.account.systems:
			self.users.append(db.get(db.Key(account)))

		if len(self.users) == 1:
			self.single = True
		else:
			self.single = False
		"""
	def account(self):
		if self._account:
			return self._account

		self._account = datamodel.DBAccounts().gql("WHERE user = :1", self.user).get()
		if not self._account:
			self._account = datamodel.DBAccounts(key_name = "acc_%s" % self.user.user_id())
			self._account.user = self.user
			self._account.name = u"Имя не задано"
			self._account.systems = []
			self._account.put()

		return self._account

	"""
	def single(self):
		if len(self.account.systems) == 1:
			self.single = True
		else:
			self.single = False
	"""

	def write_template(self, values, alturl=None):
		if self.user:
			#url = users.create_logout_url(self.request.uri)
			login_url = users.create_login_url(self.request.uri)
			values['login_url'] = login_url
			values['username'] = self.user.nickname()
			values['admin'] = users.is_current_user_admin()
			values['server_name'] = SERVER_NAME
			values['account'] = self.account
			#values['single'] = self.single
			values['self'] = self
			values['user'] = self.user
			#values['users'] = self.users
			#values['ausers'] = ausers
			#if 'imei' not in values: values['imei'] = self.uimei

			if alturl:
				path = os.path.join(os.path.dirname(__file__), 'templates', alturl)
			else:
				path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.html')
			#self.response.headers['Content-Type']   = 'text/xml'
			self.response.out.write(template.render(path, values))
		else:
			#self.response.out.write("<html><body>")
			#self.response.out.write("Для работы с системой необходимо выполнить вход под своим Google-аккаунтом.<br>")
			#self.response.out.write("Нажмите <a href=" + users.create_login_url(self.request.uri) + ">[ выполнить вход ]</a> для того чтобы перейти на сайт Google для ввода логина/пароля.<br>")
			#self.response.out.write("После ввода логина/пароля вы будете возврыщены на сайт системы.")
			#self.response.out.write("</body></html>")
			self.redirect(users.create_login_url(self.request.uri))


class MainPage(TemplatedPage):
	def get(self):
		template_values = {}
		template_values['now'] = datetime.now()
		self.write_template(template_values)

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
		greeting = datamodel.Greeting()

		if users.get_current_user():
			greeting.author = users.get_current_user()

		greeting.content = self.request.get('content')
		greeting.put()
		self.redirect('/')

def getUser(request, create=False):
#	logging.debug(uimei)
	ukey = request.get('ukey')
	if ukey:
		#userdb = datamodel.DBUser().get_by_key_name(ukey)
		userdb = db.get(db.Key(ukey))
		logging.info("GET by key: %s -> %s" % (ukey, userdb))
		return userdb
#	uid = request.get('uid')
#	if uid:
#		userdb = DBUser().get_by_id(long(uid))
		#self.response.out.write('Get by id (%d)\r\n' % userid)
	uimei = request.get('imei')
	if uimei:
		userdbq = datamodel.DBUser().all().filter('imei =', uimei).fetch(1)
		#userdbq = datamodel.DBUser().all().filter('imei =', uimei).get()
		if userdbq:
			userdb = userdbq[0] 

			uphone = request.get('phone')
			if uphone:
				if userdb.phone != uphone:
					userdb.phone = uphone
					userdb.put()

			#self.response.out.write('Get by imei (%s)\r\n' % uimei)
		else:
			if create:
				uphone = request.get('phone')
				udesc = request.get('desc')

				userdb = datamodel.DBUser()
				userdb.imei = uimei
				if uphone:
					userdb.phone = uphone
				else:
					userdb.phone = 'unknown'
				if udesc:
					userdb.desc = udesc
				else:
					userdb.desc = u'Нет описания'

				userdb.put()
			else:
				userdb = None
			#self.response.out.write('User not found by imei (%s)\r\n' % uimei)
	else:
		userdb = None

	return userdb

def get_loglastkey(user_key):
	counter = memcache.get("lastlogkey_%s" % user_key)
	if counter is not None:
		logging.info("GET Memcache key: lastlogkey_%s = %s" % (user_key, counter))
		return counter
	else:
		userdb = db.get(db.Key(user_key))
		gpslogsq = datamodel.GPSLogs.all().filter('user =', userdb).order('-date').fetch(1)
		if gpslogsq:
			counter = gpslogsq[0].key()
			memcache.add("lastlogkey_%s" % user_key, counter)
			logging.info("ADD Memcache key: lastlogkey_%s = %s" % (user_key, counter))
			return counter
		else:
			return "None"

def set_loglastkey(user_key, counter):
	memcache.set("lastlogkey_%s" % user_key, counter)
	logging.info("SET Memcache key: lastlogkey_%s = %s" % (user_key, counter))


class AddLog(webapp.RequestHandler):
	def get(self):
		#self.response.headers['Content-Type'] = 'text/plain'	#minimizing data
		self.response.headers['Content-Type'] = 'application/octet-stream'
		userdb = getUser(self.request, create=True)

		#uimei = self.request.get('imei')
		#ukey = self.request.get('ukey')
		#uid = self.request.get('uid')
		text = self.request.get('text')

		#if uid:
		#    userdb = datamodel.DBUser().get_by_id(long(uid))
		#    self.response.out.write('Get by id (%d)\r\n' % userid)

		#if uimei:
		#	userdbq = datamodel.DBUser().all().filter('imei =', uimei).fetch(2)
		#	if userdbq:
		#		userdb = userdbq[0] 
		#		self.response.out.write('Get by imei (%s)\r\n' % uimei)
		#	else:
		#		userdb = None
		#		self.response.out.write('User not found by imei (%s)\r\n' % uimei)

		newconfigs = datamodel.DBNewConfig().all().filter('user = ', userdb).fetch(1)
		if newconfigs:
			self.response.out.write('CONFIGUP\r\n')

		if userdb:
			gpslog = datamodel.GPSLogs()
			gpslog.user = userdb
			gpslog.text = text
			gpslog.put()
			set_loglastkey(str(userdb.key()), gpslog.key())
			#self.response.out.write('Add log for user (phone:%s IMEI:%s).\r\n' % (userdb.phone, userdb.imei))
			self.response.out.write('ADDLOG: OK\r\n')

		#userdb = datamodel.DBUser().get('imei', user_imei)
		#userdb = datamodel.DBUser().get_by_id(ids, parent)
		#self.response.out.write('OK.\r\n')
		#for ii in range(10):
		#    gpslog = datamodel.GPSLogs()
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
	#def post(self):
	#	userid = int(self.request.get('id'))
	#	self.response.out.write('Request body (%s)<br>' % self.request.body)
	#	file = self.request.get('file')
	#	self.response.out.write('File: %s' % file)

class UsersList(TemplatedPage):
	def get(self):
		template_values = {}

		dbusers_query = datamodel.DBUser.all().order('-date')
		dbusers = dbusers_query.fetch(50)
		dbusers_count = dbusers_query.count()
		template_values['dbusers'] = dbusers
		template_values['users_count'] = dbusers_count

		#path = os.path.join(os.path.dirname(__file__), 'users.html')
		#self.response.out.write(template.render(path, template_values))
		self.write_template(template_values)

MAXLOGS = 30

class CacheUser:
	def hello(self):
		return "Hello, from user_function"

class JsonLogs(webapp.RequestHandler):
	def get(self):
		#userdb = getUser(self.request, create=False)
		ukey = self.request.get('ukey')
		lastlogkey = self.request.get('lastlogkey')
		if lastlogkey:
			last_key = db.Key(lastlogkey)

		#if userdb == None:
		#	if len(self.account.systems)==1:
		#		userdb = db.get(db.Key(self.account.systems[0]))
		#		uimei = userdb.imei
			
		#gpslogsq = datamodel.GPSLogs.all().filter('key >', lastlogkey).filter('user =', userdb).order('-date').fetch(MAXLOGS+1)

		#if lastlogkey and get_loglastkey(str(userdb.key())) == last_key:
		if lastlogkey and get_loglastkey(ukey) == last_key:
			logging.info("No logs changes.")
			gpslogsq = []
		else:
			userdb = db.get(db.Key(ukey))
			gpslogsq = datamodel.GPSLogs.all().filter('user =', userdb).order('-date')

		gpslogs = []

		max = 20
		for gpslog in gpslogsq:
			if lastlogkey:
				if gpslog.key() == last_key: break

			gpslogs.append({
				'date': fromUTC(gpslog.date).strftime("%d/%m/%Y %H:%M:%S"),
				'text': gpslog.text,
				'key': str(gpslog.key()),
			})

			if max > 0: max = max - 1
			else: break


		"""
		if lastlogkey:
			if get_loglastkey(str(userdb.key())) == last_key:
				logging.info("No logs changes.")
				gpslogsq = []
			else:
				gpslogsq = datamodel.GPSLogs.all().filter('user =', userdb).filter('__key__ >', last_key).order('__key__').fetch(MAXLOGS+1)
		else:
			gpslogsq = datamodel.GPSLogs.all().filter('user =', userdb).order('-date').fetch(MAXLOGS+1)
		gpslogs = []
		for gpslog in gpslogsq:
			gpslogs.append({
				'date': fromUTC(gpslog.date).strftime("%d/%m/%Y %H:%M"),
				'text': gpslog.text,
				'key': str(gpslog.key()),
			})
		"""		
		self.response.headers['Content-Type']   = 'text/javascript; charset=utf-8'
		callback = self.request.get('callback')
		jsonresp = {
			"responseData": {
				#"user": uimei,
				#"counter": 1,
				#"lastkey": str(get_loglastkey(str(userdb.key()))),
				"logs": gpslogs,
			}
		}

		nejson = json.dumps(jsonresp)
		self.response.out.write(callback + "(" + nejson + ")\r")

class ViewLogs2(TemplatedPage):
	def get(self):
		#gpslogs_query = datamodel.GPSLogs.all().order('-date').fetch(MAXLOGS+1)
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
		uimei = self.request.get('imei')
		cmd = self.request.get('cmd')

		if cmd:
			if cmd=="delmsg":
				key = self.request.get('key')
				db.get(db.Key(key)).delete()


			if uimei:
				self.redirect('/logs?imei=%s' % uimei)
			else:
				self.redirect('/logs')
			

		userdb = getUser(self.request, create=False)

		if userdb == None:
			if len(self.account.systems)==1:
				userdb = db.get(db.Key(self.account.systems[0]))
				uimei = userdb.imei


		#datemark = datetime(2009, 12, 23, 21, 0, 0)
		#datemark = datetime("2009-12-23 21:10:59.140000")
		#datemark = datetime.strptime(

		if prevmark:
			if prevmark == '0':
				if uimei:
					urlprev = '<a class="Prev" href="logs?imei=%s">First</a>' % uimei
				else:
					urlprev = '<a class="Prev" href="logs">First</a>'
			else:
				if uimei:
					urlprev = '<a class="Prev" href="logs?imei=%s&date=%s&prev=0">Prev</a>' % (uimei, prevmark)
				else:
					urlprev = '<a class="Prev" href="logs?date=%s&prev=0">Prev</a>' % prevmark
		else:
			urlprev = ''

		if datemark:
			if uimei:
				gpslogs = datamodel.GPSLogs.all().filter('user =', userdb).filter('date <=', toUTC(datetime.strptime(datemark, "%Y%m%d%H%M%S"))).order('-date').fetch(MAXLOGS+1)
			else:
				gpslogs = datamodel.GPSLogs.all().filter('date <=', toUTC(datetime.strptime(datemark, "%Y%m%d%H%M%S"))).order('-date').fetch(MAXLOGS+1)
			#urlprev = '<a href="logs?date=%s">Prev</a> %s ' % (gpslogs[0].date.strftime("%d-%m-%y %H:%M:%S.%f"), datemark)  
		else:
			if uimei:
				gpslogs = datamodel.GPSLogs.all().filter('user =', userdb).order('-date').fetch(MAXLOGS+1)
			else:
				#gpslogs = datamodel.GPSLogs.all().order('-date').fetch(MAXLOGS+1)
				gpslogs = []
				"""
				gpslogsq = datamodel.GPSLogs.all().order('-date')
				gpslogs = []
				i = MAXLOGS+1
				for gpslog in gpslogsq:
					if str(gpslog.user.key()) in self.account.systems:
						gpslogs.append(gpslog)
						i = i - 1
						if i <= 0: break
				"""
		gpslogs_count = len(gpslogs)
		if gpslogs_count == MAXLOGS+1:
			if datemark:
				if uimei:
					urlnext = '<a class="Next" href="logs?imei=%s&date=%s&prev=%s">Next</a> ' % (uimei, fromUTC(gpslogs[-1].date).strftime("%Y%m%d%H%M%S"), datemark)
				else:
					urlnext = '<a class="Next" href="logs?date=%s&prev=%s">Next</a> ' % (fromUTC(gpslogs[-1].date).strftime("%Y%m%d%H%M%S"), datemark)
			else:
				if uimei:
					urlnext = '<a class="Next" href="logs?imei=%s&date=%s&prev=0">Next</a>' % (uimei, fromUTC(gpslogs[-1].date).strftime("%Y%m%d%H%M%S"))
				else:
					urlnext = '<a class="Next" href="logs?date=%s&prev=0">Next</a>' % fromUTC(gpslogs[-1].date).strftime("%Y%m%d%H%M%S")
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

		#userdescs = {}
		#userimeis = {}

		for gpslog in gpslogs:
			#gpslog.date = gpslog.date.replace(microsecond=0).replace(second=0)
			gpslog.sdate = fromUTC(gpslog.date).strftime("%d/%m/%Y %H:%M:%S")
			#if gpslog.user.key() not in userdescs:
			#	userdescs[gpslog.user.key()] = gpslog.user.desc
			#	userimeis[gpslog.user.key()] = gpslog.user.imei
			#gpslog.desc = userdescs[gpslog.user.key()]
			#gpslog.imei = userimeis[gpslog.user.key()]
			#gpslog.desc = gpslog.user.desc
			#gpslog.imei = gpslog.user.imei
			#geolog.date = fromUTC(geolog.date) #.astimezone(utc)

			#try:
			#	uuser = gpslog.user
			#	gpslog.imei = uuser.imei
			#except:
			#	gpslog.imei = 'deleted' 
			#if not gpslog.user:
			#    gpslog.user.imei = "deleted"

		template_values = {}
		template_values['gpslogs'] = gpslogs
		template_values['urlnext'] = urlnext
		template_values['urlprev'] = urlprev
		template_values['userdb'] = userdb
		if userdb:
			template_values['userkey'] = str(userdb.key())
		else:
			template_values['userkey'] = "None"
		template_values['imei'] = uimei
		#template_values['loglastkey'] = get_loglastkey()
		#template_values['loglastkey']

		cacheuser = CacheUser()
		template_values['cacheuser'] = cacheuser

		#path = os.path.join(os.path.dirname(__file__), 'logs.html')
		#self.response.out.write(template.render(path, template_values))


		logs = ':'
		if userdb:
			for vlogs in userdb.logs:
				logs += '<p>' + vlogs.text + '</p>'
		"""
		a_ViewLogs = datamodel.DBUser().all().fetch(10)
		for viewlog in a_ViewLogs:
			logs += '<br/>' + viewlog.imei
			for vlogs in viewlog.logs:
				logs += '<p>' + vlogs.text + '</p>'
			pass
		template_values['ldebug'] = a_ViewLogs
		"""
		template_values['ldebug_logs'] = logs

		self.write_template(template_values)

		#try:
		#	self.response.out.write(template.render(path, template_values))
		#except:
		#	self.response.out.write("<html><body>Database error</body></html>")
		#self.response.out.write(template.generate(path, template_values))
		#self.generate()


class ViewLogs(TemplatedPage2):
	def get(self):
		userdb = getUser(self.request, create=False)
		if userdb == None:
			template_values = {}
			#os.environ['TZ'] = 'America/Los_Angeles'
			#template_values['now'] = datetime.now()
			self.write_template(template_values)
			return

		ukey = str(userdb.key())

		#datemark = self.request.get('date')
		#prevmark = self.request.get('prev')
		#uimei = self.request.get('imei')
		cmd = self.request.get('cmd')

		if cmd:
			if cmd=="delmsg":
				key = self.request.get('key')
				db.get(db.Key(key)).delete()

			self.redirect('/logs2?ukey=%s' % ukey)

		q = userdb.logs.order('-date')
		cursor = self.request.get('cursor')
		if cursor:
			q.with_cursor(cursor)

		#gpslogs = userdb.logs.order('-date').fetch(MAXLOGS+1)
		logs = q.fetch(MAXLOGS+1)
		"""
		for gpslog in gpslogs:
			#gpslog.date = gpslog.date.replace(microsecond=0).replace(second=0)
			gpslog.sdate = fromUTC(gpslog.date).strftime("%d/%m/%Y %H:%M:%S")
			#if gpslog.user.key() not in userdescs:
			#	userdescs[gpslog.user.key()] = gpslog.user.desc
			#	userimeis[gpslog.user.key()] = gpslog.user.imei
			#gpslog.desc = userdescs[gpslog.user.key()]
			#gpslog.imei = userimeis[gpslog.user.key()]
			#gpslog.desc = gpslog.user.desc
			#gpslog.imei = gpslog.user.imei
			#geolog.date = fromUTC(geolog.date) #.astimezone(utc)

			#try:
			#	uuser = gpslog.user
			#	gpslog.imei = uuser.imei
			#except:
			#	gpslog.imei = 'deleted' 
			#if not gpslog.user:
			#    gpslog.user.imei = "deleted"
		"""
		template_values = {}
		template_values['logs'] = logs
		template_values['userdb'] = userdb
		#template_values['userkey'] = str(userdb.key())
		#template_values['imei'] = uimei
		#template_values['imei'] = userdb.imei
		template_values['ukey'] = ukey
		template_values['ncursor'] = q.cursor()
		#template_values['loglastkey'] = get_loglastkey()
		#template_values['loglastkey']

		cacheuser = CacheUser()
		template_values['cacheuser'] = cacheuser

		#path = os.path.join(os.path.dirname(__file__), 'logs.html')
		#self.response.out.write(template.render(path, template_values))
		"""
		logs = ':'
		if userdb:
			for vlogs in userdb.logs:
				logs += '<p>' + vlogs.text + '</p>'
		template_values['ldebug_logs'] = logs
		"""
		

		self.write_template(template_values)

		#try:
		#	self.response.out.write(template.render(path, template_values))
		#except:
		#	self.response.out.write("<html><body>Database error</body></html>")
		#self.response.out.write(template.generate(path, template_values))
		#self.generate()


class DelLogs(webapp.RequestHandler):
	def get(self):
		logs = datamodel.GPSLogs.all().order('date').fetch(100)
		for log in logs:
			log.delete()
		self.redirect("/logs")

"""
class RegId(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'    #minimizing data
		imei = self.request.get('imei')
		phone = self.request.get('phone')
		passw = self.request.get('pass')
		self.response.out.write('imei=%s\r\nphone=%s\r\npass=%s\r\n' % (imei, phone, passw))

		#users = db.Query(DBUser).filter('phone', phone).fetch(2)
		users = db.Query(datamodel.DBUser).filter('imei', imei).fetch(2)

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
			newuser = datamodel.DBUser()
			newuser.imei = imei
			newuser.phone = phone
			newuser.password = passw
			newuser.put()
			self.response.out.write('User added.\r\n')

		ukey = newuser.key()

		self.response.out.write('key=%s\r\n' % ukey)
		self.response.out.write('id=%s\r\n' % ukey.id())
"""
class DelUser(webapp.RequestHandler):
	def get(self):
		ukey = self.request.get('key')
		uid = self.request.get('id')
		#duser = datamodel.DBUser().get_by_key_name(cls, key_names, parent)
		if ukey:
			db.delete(db.Key(ukey))

		if uid:
			userdb = datamodel.DBUser().get_by_id(long(uid))
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
			speed = float(self.request.get('speed')) * 1.852	# переведем в км/ч
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

			gpspoint = datamodel.DBGPSPoint()
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


'''
class Pacific_tzinfo(tzinfo):
 """Implementation of the Pacific timezone."""
 def utcoffset(self, dt):
   return datetime_module.timedelta(hours=-8) + self.dst(dt)

 def _FirstSunday(self, dt):
   """First Sunday on or after dt."""
   return dt + datetime_module.timedelta(days=(6-dt.weekday()))

 def dst(self, dt):
   # 2 am on the second Sunday in March
   dst_start = self._FirstSunday(datetime_module.datetime(dt.year, 3, 8, 2))
   # 1 am on the first Sunday in November
   dst_end = self._FirstSunday(datetime_module.datetime(dt.year, 11, 1, 1))

   if dst_start <= dt.replace(tzinfo=None) < dst_end:
     return datetime_module.timedelta(hours=1)
   else:
     return datetime_module.timedelta(hours=0)

 def tzname(self, dt):
   if self.dst(dt) == datetime_module.timedelta(hours=0):
     return "PST"
   else:
     return "PDT"

#pacific_time = utc_time.astimezone(Pacific_tzinfo())
'''

class Geos(TemplatedPage2):
	def get(self):
		userdb = getUser(self.request, create=False)
		if userdb == None:
			template_values = {}
			self.write_template(template_values)
			return

		ukey = str(userdb.key())

		cursor = self.request.get('cursor')
		#geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).order('-date').fetch(MAXLOGS+1)
		q = userdb.geos.order('-date')

		if cursor:
		    q.with_cursor(cursor)

		geologs = q.fetch(MAXLOGS+1)
		#geologs = q.fetch(10)
		#geologs = userdb.geos.order('-date').fetch(MAXLOGS+1)

		#geologs = datamodel.DBGPSPoint.all().order('-date').fetch(100)
		"""
		for geolog in geologs:
			#try:
			#	uuser = geolog.user
			#	geolog.imei = uuser.imei
			#except:
			#	geolog.imei = 'deleted'
			#geolog.sdate = geolog.cdate.strftime("%d/%m/%Y %H:%M")
			geolog.date = fromUTC(geolog.date) #.astimezone(utc)
			#if geolog.vin == None:
			#	geolog.vin = 0.0
			#if geolog.vout == None:
			#	geolog.vout = 0.0
		"""

		"""
		for geolog in geologs:
			lat = geolog.latitude
			deg = int(lat)
			lat = (lat-deg)*60.0
			min = int(lat)
			lat = (lat-min)*60.0
			sec = int(lat)
			lat = (lat-sec)*60.0
			part = int(lat)
			geolog.latitudeams = '%02dº%02d\'%02d\'\'%02d' % (deg, min, sec, part)

			lat = geolog.latitude
			if lat<0: lat = -lat;
			deg = int(lat)
			lat = (lat-deg)*60.0
			geolog.latitudegps = '%02d%07.4f' % (deg, lat)
			if geolog.latitude>=0: geolog.latitudegps += 'N'
			else: geolog.latitudegps += 'S'

			lat = geolog.longitude
			deg = int(lat)
			lat = (lat-deg)*60.0
			min = int(lat)
			lat = (lat-min)*60.0
			sec = int(lat)
			lat = (lat-sec)*60.0
			part = int(lat)
			geolog.longitudeams = '%03dº%02d\'%02d\'\'%02d' % (deg, min, sec, part)

			lat = geolog.longitude
			if lat<0: lat = -lat;
			deg = int(lat)
			lat = (lat-deg)*60.0
			geolog.longitudegps = '%03d%07.4f' % (deg, lat)
			if geolog.longitude>=0: geolog.longitudegps += 'E'
			else: geolog.longitudegps += 'W'

		#<td title="({{ geolog.latitudeams }}) ({{ geolog.latitudegps }})">{{ geolog.latitude|floatformat:6 }}</td>
		#<td title="({{ geolog.longitudeams }}) ({{ geolog.longitudegps }})">{{ geolog.longitude|floatformat:6 }}</td>
		"""


		#path = os.path.join(os.path.dirname(__file__), 'geos.html')
		#self.response.out.write(template.render(path, template_values))
		template_values = {}
		template_values['geologs'] = geologs
		#template_values['imei'] = userdb.imei
		template_values['ukey'] = ukey
		template_values['userdb'] = userdb
		template_values['ncursor'] = q.cursor()

		#self.write_template({'geologs': geologs, 'imei': uimei, 'userdb': userdb})
		self.write_template(template_values)


class Geos2(TemplatedPage):
	def get(self):
		#uimei = self.request.get('imei')
		userdb = getUser(self.request)

		if userdb == None:
			if len(self.account.systems)==1:
				userdb = db.get(db.Key(self.account.systems[0]))
				uimei = userdb.imei
				geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).order('-date').fetch(MAXLOGS+1)
			else:
				#geologs = datamodel.DBGPSPoint.all().order('-date').fetch(MAXLOGS+1)
				geologs = []
		else:
			geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).order('-date').fetch(MAXLOGS+1)

		#geologs = datamodel.DBGPSPoint.all().order('-date').fetch(100)
		for geolog in geologs:
			#try:
			#	uuser = geolog.user
			#	geolog.imei = uuser.imei
			#except:
			#	geolog.imei = 'deleted'
			#geolog.sdate = geolog.cdate.strftime("%d/%m/%Y %H:%M")
			geolog.date = fromUTC(geolog.date) #.astimezone(utc)
			if geolog.vin == None:
				geolog.vin = 0.0
			if geolog.vout == None:
				geolog.vout = 0.0

		#path = os.path.join(os.path.dirname(__file__), 'geos.html')
		#self.response.out.write(template.render(path, template_values))
		self.write_template({'geologs': geologs, 'userdb': userdb})

class GetTrack(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		uimei = self.request.get('imei')
		userdb = getUser(self.request)

		if userdb == None:
			geologs = datamodel.DBGPSPoint.all().order('-date').fetch(MAX_TRACK_FETCH)
			#geologs = datamodel.DBGPSPoint.all().order('-date').fetch(10)
		else:
			geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).order('-date').fetch(MAX_TRACK_FETCH)
			#geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).order('-date').fetch(10)
		points = []
		for geolog in geologs:
			points.append({
				'date': geolog.date,	#.strftime("%d/%m/%Y %H:%M:%S"),
				'lat': geolog.latitude,
				'long': geolog.longitude,
				'speed': geolog.speed
			})
		self.response.out.write(repr(points))

def dec2angle_real(x, y):
	if x==0 and y==0:
		return -1.0
	if x==0:
		if y>0.0: return 90
		else: return 270
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


class GeosJSON(webapp.RequestHandler):
	def get(self):
		#start_time = datetime.now()
		#logging.info("GeosJSON start (%s)" % start_time.strftime("%H:%M:%S"))

		callback = self.request.get('callback')

		self.response.headers['Content-Type']   = 'text/javascript; charset=utf-8'

		userdb = getUser(self.request)
		if userdb == None:
			uaccount = self.request.get('account')
			user = None
			if uaccount:
				user = users.User(uaccount)
				if not user:
					logging.info("User not found.")
			else:
				logging.info("Not defined 'account'.")

			account = datamodel.DBAccounts().gql("WHERE user = :1", user).get()
			results = []
			if account:
				for system in account.users:
					item = {
						"imei": system.imei,
						"desc": system.desc,
						"phone": system.phone,
					}
					geolog = system.geos.order('-date').get()
					if geolog:
						item["lastpos"] = {
							"date": fromUTC(geolog.date).strftime("%d/%m/%Y %H:%M:%S"),
							#"localdate": geolog.date.strftime("%d/%m/%Y %H:%M:%S"),
							#"day": geolog.date.strftime("%m/%d/%Y %H:%M"),
							"lat": geolog.latitude,
							"long": geolog.longitude,
							"sats": geolog.sats,
							"fix": geolog.fix,
							"speed": geolog.speed,
							"course": geolog.course,
							"alt": geolog.altitude,
							"in1": geolog.in1,
							"in2": geolog.in2,
							"vin": geolog.vin,
							"vout": geolog.vout,
						}
					else:
						item["lastpos"] = None

					results.append(item)
			else:
				logging.info("Account not found.")

			jsonresp = {
				"responseData": {
					"results": results, 
					"count": len(account.users),
					"config": 0,
					"username": user.nickname(),
				}
			}
			nejson = json.dumps(jsonresp)
			self.response.out.write(callback + "(" + nejson + ")\r")
			return

		#dif_time = datetime.now() - start_time
		#logging.info("GeosJSON user ready (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))

		datefrom_s = self.request.get('datefrom')
		if datefrom_s:
			datefrom = toUTC(datetime.strptime(datefrom_s, "%d%m%Y%H%M%S"))
		else:
			datefrom = datetime.now()

		#logging.info("GeosJSON datefrom: %s" % datefrom)

		dateto_s = self.request.get('dateto')
		if dateto_s:
			dateto = toUTC(datetime.strptime(dateto_s, "%d%m%Y%H%M%S"))
		else:
			dateto = datetime.now()

		#logging.info("GeosJSON dateto: %s" % dateto)

		first = self.request.get('first')
		if first:
			#logging.info("GeosJSON first: %s" % first)
			if datefrom_s:
				geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).filter('date >=', datefrom).order('date').fetch(int(first))
				#geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).filter('date >=', datefrom).order('date').fetch(4)
			else:
				geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).order('date').fetch(int(first))
				#geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).order('date').fetch(4)
				pass
		else:
			last = self.request.get('last')
			if last:
				#logging.info("GeosJSON last: %s" % last)
				#geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).filter('date <=', dateto).order('-date').fetch(int(last))
				geologs = userdb.geos.filter('date <=', dateto).order('-date').fetch(int(last))
			else:
				#geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).filter('date >=', datefrom).filter('date <=', dateto).order('-date').fetch(MAX_TRACK_FETCH)
				#geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).filter('date >=', datefrom).filter('date <=', dateto).order('-date').fetch(4)
				if datefrom_s:
					#geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).filter('date >=', datefrom).order('date').fetch(int(first))
					geologs = userdb.geos.filter('date <=', dateto).filter('date >=', datefrom).order('-date').fetch(MAX_TRACK_FETCH)
				else:
					geologs = userdb.geos.filter('date <=', dateto).order('-date').fetch(MAX_TRACK_FETCH)
				
		#geologs = {}
		#self.response.out.write("// User imei: %s\r// Date from: %s\r// Date to: %s\r" % (userdb.imei, datefrom, dateto))

#.filter('date <=', datetime.strptime(datemark, "%Y%m%d%H%M%S%f"))
		#geologs = DBGPSPoint.all().order('-date').filter('user =', userdb)
		#geologs = DBGPSPoint.all().order('-date').fetch(MAX_TRACK_FETCH)
		#geologs = DBGPSPoint.all().order('-date').fetch(MAXLOGS+1)

		optim = self.request.get('optim')

		#dif_time = datetime.now() - start_time
		#logging.info("GeosJSON db ready (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))

		results = []
		if geologs:
			if not first:
				#dif_time = datetime.now() - start_time
				#logging.info("Start reverse (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))
				geologs.reverse()
				#logging.info("Stop reverse (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))

		prev_lat = 0.0
		prev_long = 0.0
		prev_course = 0.0
		#MIN_QDELTA = 0.00001
		MIN_QDELTA = 0.01 * 0.01	# 1км?
		ADELTA = 10.0
		MIN_ADELTA = 5.0
		TAN5 = 0.08748	# tan(5град)

		for geolog in geologs:

			#a1 = 0.0
			if optim:
				if geolog.speed < 0.1: continue

				delta_lat = math.fabs(geolog.latitude - prev_lat)
				delta_long = math.fabs(geolog.longitude - prev_long) * math.cos(geolog.latitude * math.pi / 180.0)

				delta_course = math.fabs(geolog.course - prev_course)
				if delta_course > 180.0:
					delta_course = 360.0 - delta_course
				if delta_course < ADELTA:
					if ADELTA > MIN_ADELTA:
						ADELTA = ADELTA - 1
					if (delta_lat*delta_lat + delta_long*delta_long) < MIN_QDELTA:
						continue

				# Дополнительная попытка исправить небольшие зигзаги на длинных прямых
				#if len(results) >= 2:
				#	dx1 = geolog.latitude - results[-1]["lat"]
				#	dy1 = geolog.longitude - results[-1]["long"]
				#	a1 = dec2angle(dx1, dy1)
				#
				#	dx2 = results[-1]["lat"] - results[-2]["lat"]
				#	dy2 = results[-1]["long"] - results[-2]["long"]
				#	a2 = dec2angle(dx2, dy2)
				#
				#	deltaa = math.fabs(a2-a1)
				#	if deltaa > 180.0: deltaa = 360.0 - deltaa
				#	if deltaa < 1.0: continue

				prev_course = geolog.course
				prev_lat = geolog.latitude
				prev_long = geolog.longitude
				ADELTA = 10.0

			result = {
				#"date": geolog.date.strftime("%d/%m/%Y %H:%M:%S"),
				#"localdate": fromUTC(geolog.date).strftime("%d/%m/%Y %H:%M:%S"),
				"date": fromUTC(geolog.date).strftime("%d/%m/%Y %H:%M:%S"),
				#"localdate": geolog.date.strftime("%d/%m/%Y %H:%M:%S"),
				#"day": geolog.date.strftime("%m/%d/%Y %H:%M"),
				"lat": geolog.latitude,
				"long": geolog.longitude,
				"sats": geolog.sats,
				"fix": geolog.fix,
				"speed": geolog.speed,
				"course": geolog.course,
				"alt": geolog.altitude,
				"in1": geolog.in1,
				"in2": geolog.in2,
				"vin": geolog.vin,
				"vout": geolog.vout,
				"fsourced": geolog.fsourced,
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
			#if first:
				jsonresp = {
					"responseData": {
						"results": results, 
						"config": 0,
						"dateminjs": fromUTC(geologs[0].date).strftime("%m/%d/%Y %H:%M"),
						"datemaxjs": fromUTC(geologs[-1].date).strftime("%m/%d/%Y %H:%M"),
						"datemin": fromUTC(geologs[0].date).strftime("%d/%m/%Y %H:%M:%S"),
						"datemax": fromUTC(geologs[-1].date).strftime("%d/%m/%Y %H:%M:%S"),
					}
				}
			#else:
			#	jsonresp = {
			#		"responseData": {
			#			"results": results, 
			#			"config": 0,
			#			"dateminjs": geologs[-1].date.strftime("%m/%d/%Y %H:%M"),
			#			"datemaxjs": geologs[0].date.strftime("%m/%d/%Y %H:%M"),
			#			"datemin": geologs[-1].date.strftime("%d/%m/%Y %H:%M:%S"),
			#			"datemax": geologs[0].date.strftime("%d/%m/%Y %H:%M:%S"),
			#		}
			#	}
		else:
			jsonresp = {
				"responseData": {
					"results": results, 
					"config": 0,
				}
			}
		
		#dif_time = datetime.now() - start_time
		#logging.info("GeosJSON response ready (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))

		nejson = json.dumps(jsonresp)
		self.response.out.write(callback + "(" + nejson + ")\r")

		#dif_time = datetime.now() - start_time
		#logging.info("GeosJSON json-out ready (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))

		#logging.info("GeosJSON data: %d values" % len(results))

		return

class DelGeos(webapp.RequestHandler):
	def get(self):
		uimei = self.request.get('imei')
		datefrom_s = self.request.get('datefrom')
		if datefrom_s:
			datefrom = toUTC(datetime.strptime(datefrom_s, "%d%m%Y%H%M%S"))

		dateto_s = self.request.get('dateto')
		if dateto_s:
			dateto = toUTC(datetime.strptime(dateto_s, "%d%m%Y%H%M%S"))

		userdb = getUser(self.request)

		if datefrom_s:
			logging.info("Deleting data from %s to %s 4 user %s" % (datefrom, dateto, uimei))
			if userdb == None:
				geologs = datamodel.DBGPSPoint.all().filter('date >=', datefrom).filter('date <=', dateto).order('date').fetch(MAX_TRACK_FETCH)
			else:
				geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).filter('date >=', datefrom).filter('date <=', dateto).order('date').fetch(MAX_TRACK_FETCH)
			logging.info("Delete %d items" % len(geologs))
			if geologs:
				db.delete(geologs)
			if userdb:
				self.redirect("/maps?ukey=%s" % userdb.key())
			else:
				self.redirect("/maps")
		else:
			logging.info("Deleting old data 4 user %s" % uimei)
			if userdb == None:
				geologs = datamodel.DBGPSPoint.all().order('date').fetch(MAX_TRACK_FETCH)
			else:
				geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).order('date').fetch(MAX_TRACK_FETCH)

			if geologs:
				db.delete(geologs)
			if userdb:
				self.redirect("/geos?ukey=%s" % userdb.key())
			else:
				self.redirect("/geos")

class Del1Geos(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type']   = 'text/javascript; charset=utf-8'
		callback = self.request.get('callback')

		uimei = self.request.get('imei')
		datepoint = self.request.get('datetime')
		if datepoint:
			datepoint = toUTC(datetime.strptime(datepoint, "%d%m%Y%H%M%S"))

		logging.info("Delete 1 GPS point %s" % datepoint)

		geologs = datamodel.DBGPSPoint.all().filter('date ==', datepoint).fetch(2)
		if geologs:
			logging.info("OK key=%s" % geologs[0].key())
			geologs[0].delete()
		else:
			logging.info("ERROR point not found")

		jsonresp = {
			"responseData": {
				"answer": "ok",
			}
		}

		nejson = json.dumps(jsonresp)
		self.response.out.write(callback + "(" + nejson + ")\r")

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

def sortDict(adict):
	keys = sorted(adict.keys())
	#keys.sort()
	logging.info(repr(keys))
	return [(key, adict[key]) for key in keys]
	#return map(adict.get, keys)

class Config(TemplatedPage):
	def get(self):
		cmd = self.request.get('cmd')
		uimei = self.request.get('imei')

		if cmd == 'addsys':
			uphone = self.request.get('phone')

			logging.info("== ADD SYS ==")
			oper = "undef"

			# Сначала проверим введенные данные (есть ли такая система в базе)
			userdb = None
			if uimei:
				userdbq = datamodel.DBUser().all().filter('imei =', uimei).fetch(1)
				if userdbq:
					userdb = userdbq[0]
			if not userdb:
				#if uphone and (len(uphone)>0):
				if uphone and (uphone != ""):
					userdbq = datamodel.DBUser().all().filter('phone =', uphone).fetch(1)
					if userdbq:
						userdb = userdbq[0]
			if userdb:
				#Теперь посмотрим не наблюдаем ли мы уже эту систему
				if str(userdb.key()) in self.account.systems:
					oper = "already"
				else:
					#Не наблюдаем :)
					self.account.systems.append(str(userdb.key()))
					self.account.put()
					oper = "added"
			else:
				oper = "not found"


			self.response.headers['Content-Type']   = 'text/javascript; charset=utf-8'
			callback = self.request.get('callback')
			jsonresp = {
				"responseData": {
					"confirm": 1,
					"systems": self.account.systems,
					"result": oper,
				}
			}
			nejson = json.dumps(jsonresp)
			self.response.out.write(callback + "(" + nejson + ")\r")
			return
		elif cmd == 'delsys':
			oper="undef"
			userdbq = datamodel.DBUser().all().filter('imei =', uimei).fetch(1)
			if userdbq:
				self.account.systems.remove(str(userdbq[0].key()))
				self.account.put()
				oper = "ok"
			else:
				oper = "not found"

			callback = self.request.get('callback')
			jsonresp = {
				"responseData": {
					"confirm": 1,
					"systems": self.account.systems,
					"result": oper,
				}
			}
			nejson = json.dumps(jsonresp)
			self.response.out.write(callback + "(" + nejson + ")\r")
			return


		userdb = getUser(self.request)
		#logging.debug(userdb.imei)

		if userdb == None:
			#allusers = datamodel.DBUser.all().fetch(100)
			#accounts = datamodel.DBAccounts().all().filter('user =', self.user).fetch(1)
			#allusers = []
			#for account in self.account.systems:
			#	allusers.append(db.get(db.Key(account)))

			#path = os.path.join(os.path.dirname(__file__), 'svg', 'cars')
			#flist = os.listdir('/')

			template_values = {
				'now': datetime.now(),
				#'path': path,
				#'flist': flist,
			}

			#path = os.path.join(os.path.dirname(__file__), 'templates/config.html')
			#self.response.out.write(template.render(path, template_values))

			#template_values = {}
			self.write_template(template_values)
		else:
			if cmd == 'last':
				#self.response.out.write('<html><head><link type="text/css" rel="stylesheet" href="stylesheets/main.css" /></head><body>CONFIG:<br><table>')
				#self.response.out.write(u"<tr><th>Имя</th><th>Тип</th><th>Значение</th><th>Заводская установка</th></tr>" )

				showall = self.request.get('showall')

				descriptions = datamodel.DBDescription().all() #.fetch(MAX_TRACK_FETCH)

				descs={}
				fdescs={}
				for description in descriptions:
					descs[description.name] = description.value
					fdescs[description.name] = description
					pass

				newconfig = datamodel.DBConfig().all().filter('user = ', userdb).fetch(1)
				#for dbconfig in newconfig:
				if newconfig:
					#self.response.out.write("<tr><th>date: %s</th></tr>" % dbconfig.cdate)
					configs = eval(zlib.decompress(newconfig[0].config))
					#configs = sortDict(eval(zlib.decompress(newconfig[0].config)))

					#configs = eval(dbconfig.strconfig)

					#try:
					#	for config, value in configs.items():
					#		self.response.out.write("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (config, value[0], value[1], value[2]))
					#except:
					#	self.response.out.write("<tr><td>orig:%s</td></tr>" % repr(configs))

					waitconfigs = datamodel.DBNewConfig().all().filter('user = ', userdb).fetch(1)
					if waitconfigs:
						waitconfig = eval(zlib.decompress(waitconfigs[0].config))
					else:
						waitconfig = {}

					nconfigs = {}

					for config, value in configs.items():
						#desc = u"Нет описания"
						desc = u"Нет описания"
						fdesc = None
						if config in descs:
							desc = descs[config]
							fdesc = fdescs[config]
						else:
							if not showall:
							#if not users.is_current_user_admin():
								continue

						if config in waitconfig:
							nconfigs[config] = (configs[config][0], configs[config][1], configs[config][2], waitconfig[config], desc, fdesc)
						else:
							nconfigs[config] = (configs[config][0], configs[config][1], configs[config][2], None, desc, fdesc)
							#configs[config] = (configs[config][0], configs[config][1], configs[config][2], configs[config][1])

					# Для удобства отсортируем словарь в список
					#sconfigs = sortDict(configs)
					sconfigs = [(key, nconfigs[key]) for key in sorted(nconfigs.keys())]

					template_values = {
					    'configs': sconfigs,
					    'user': userdb,
					    'imei': uimei
					}

					#path = os.path.join(os.path.dirname(__file__), 'templates/config-last.html')
					#self.response.out.write(template.render(path, template_values))
					self.write_template(template_values, alturl='config-last.html')
				else:
					self.response.out.write(u"<html><body>Нет записей</body></html>")
					#self.response.out.write("</table></body></html>")

			else:
				template_values = {
				    'configs': conf_parms,
				    'user': userdb,
				    'imei': uimei
				}

				path = os.path.join(os.path.dirname(__file__), 'templates/params.html')
				self.response.out.write(template.render(path, template_values))

		#DBNewConfig

	def post(self):
		userdb = getUser(self.request, create=True)
		if not userdb:
			self.response.out.write("NO USER")
			return

		cmd = self.request.get('cmd')
		if cmd == 'save':
			#self.response.headers['Content-Type'] = 'text/plain'	#minimizing data
			self.response.headers['Content-Type'] = 'application/octet-stream'
			newconfigs = datamodel.DBConfig().all().filter('user = ', userdb).fetch(1)
			if newconfigs:
				newconfig = newconfigs[0]
				#Подавим объединение конфигураций
				config = {}
				#config = eval(zlib.decompress(newconfig.config))
				##config = eval(newconfig.strconfig)
			else:
				newconfig = datamodel.DBConfig()
				newconfig.user = userdb
				config = {}

			#logging.info(self.request.body)
			for conf in self.request.body.split("\n"):
				params = conf.strip().split()
				#logging.info(params)
				if len(params) == 4:
					config[params[0]] = (params[1], params[2], params[3])
				#self.response.out.write("<tr><td>parts:%s</td></tr>" % repr(conf.strip()))

			#newconfig = DBConfig()
			#newconfig.user = userdb
			newconfig.config = zlib.compress(repr(config), 9)
			#newconfig.strconfig = repr(config)
			newconfig.put()

			self.response.out.write("CONFIG: OK\r\n")

			pass
		else:

			self.response.out.write("<html><body>\r\n")

			config = self.request.get('userconfig') + ";" + self.request.get('custom')
			params = config.split(';')

			self.response.out.write("Config: %s<br/>" % config)

			newconfigs = datamodel.DBNewConfig().all().filter('user = ', userdb).fetch(1)
			if newconfigs:
				newconfig = newconfigs[0]
				config = eval(zlib.decompress(newconfig.config))
				#config = eval(newconfig.strconfig)
			else:
				newconfig = datamodel.DBNewConfig()
				newconfig.user = userdb
				config = {}

			for param in params:
				item = param.split('=')
				if len(item) == 2:
					config[item[0]] = item[1]

			newconfig.config = zlib.compress(repr(config), 9)
			#newconfig.strconfig = repr(config)
			newconfig.put()

			if len(config) != 0:
				self.response.out.write("Params: %d" % len(config))

			self.response.out.write("</body></html>")
		pass


class Params(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'	#minimizing data
		cmd = self.request.get('cmd')
		uimei = self.request.get('imei')
		userdb = getUser(self.request)
		if userdb == None:
			self.response.out.write("NOUSER")
			return

		if cmd == 'params':
			self.response.headers['Content-Type'] = 'application/octet-stream'
			#self.response.out.write("<html><body>CONFIG:<br><table>")
			newconfig = datamodel.DBNewConfig().all().filter('user = ', userdb).fetch(1)
			#for dbconfig in newconfig:
			if newconfig:
				#self.response.out.write("<tr><th>date: %s</th></tr>" % dbconfig.cdate)
				configs = eval(zlib.decompress(newconfig[0].config))
				#configs = eval(dbconfig.strconfig)
				for config, value in configs.items():
					#self.response.out.write("<tr><td>%s:%s</td></tr>" % (config, value))
					self.response.out.write("PARAM %s %s\r\n" % (config, value))
				self.response.out.write("FINISH\r\n")
			else:
				self.response.out.write("NODATA\r\n")
			#self.response.out.write("</table></body></html>")
			pass

		elif cmd == 'cancel':
			newconfigs = datamodel.DBNewConfig().all().filter('user = ', userdb).fetch(100)
			for newconfig in newconfigs:
				newconfig.delete()
			self.response.out.write("DELETED")

		elif cmd == 'confirm':
			self.response.headers['Content-Type'] = 'application/octet-stream'
			newconfig = datamodel.DBNewConfig().all().filter('user = ', userdb).fetch(100)

			if newconfig:
				newconfigs = eval(zlib.decompress(newconfig[0].config))


				saveconfigs = datamodel.DBConfig().all().filter('user = ', userdb).fetch(1)
				if saveconfigs:
					saveconfig = saveconfigs[0]
					config = eval(zlib.decompress(saveconfig.config))
				else:
					saveconfig = datamodel.DBConfig()
					saveconfig.user = userdb
					config = {}

				#configs = eval(dbconfig.strconfig)
				for pconfig, pvalue in newconfigs.items():
					if pconfig in config:
						config[pconfig] = (config[pconfig][0], pvalue, config[pconfig][2])

				saveconfig.config = zlib.compress(repr(config), 9)
				saveconfig.put()

				for nc in newconfig:
					nc.delete()

				self.response.out.write("CONFIRM")

			else:
				self.response.out.write("NODATA")

		elif cmd == 'changeone':
			logging.info(" === Change one parameter")
			callback = self.request.get('callback')
			name = self.request.get('name')
			value = self.request.get('value')

			newconfigs = datamodel.DBNewConfig().all().filter('user = ', userdb).fetch(1)
			if newconfigs:
				newconfig = newconfigs[0]
				config = eval(zlib.decompress(newconfig.config))
				#config = eval(newconfig.strconfig)
			else:
				newconfig = datamodel.DBNewConfig()
				newconfig.user = userdb
				config = {}


			savedconfigs = datamodel.DBConfig().all().filter('user = ', userdb).fetch(1)
			config[name] = value
			if savedconfigs:
				savedconfig = eval(zlib.decompress(savedconfigs[0].config))
				if name in savedconfig:
					if savedconfig[name][1] == value:
						del config[name]

			newconfig.config = zlib.compress(repr(config), 9)
			#newconfig.strconfig = repr(config)
			newconfig.put()

			self.response.headers['Content-Type']   = 'text/javascript; charset=utf-8'
			jsonresp = {
				"responseData": {
					"confirm": 1,
					"name": name,
					"value": value,
				}
			}
			nejson = json.dumps(jsonresp)
			self.response.out.write(callback + "(" + nejson + ")\r")
		elif cmd == 'check':
			newconfigs = datamodel.DBNewConfig().all().filter('user = ', userdb).fetch(1)
			if newconfigs:
				self.response.out.write('CONFIGUP\r\n')
			else:
				self.response.out.write('NODATA\r\n')
		else:
			self.response.out.write('CMD_ERROR\r\n')


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

		#self.response.headers['Content-Type'] = 'text/plain'
		self.response.headers['Content-Type'] = 'application/octet-stream'

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

			userdb = datamodel.DBUser()
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
			newbin = datamodel.DBGPSBin()
			newbin.user = userdb
			newbin.dataid = dataid
			newbin.data = pdata #db.Text(pdata)
			newbin.put()

			_log += '\nSaving to backup'
			newbinb = datamodel.DBGPSBinBackup()
			newbinb.user = userdb
			newbinb.dataid = dataid
			newbinb.data = pdata
			newbinb.put()

			_log += '\nSaved to DBGPSBin creating tasque'

			url = "/parsebingeos?dataid=%s&key=%s" % (dataid, newbin.key())
			#taskqueue.add(url = url % self.key().id(), method="GET", countdown=countdown)
			countdown=0
			taskqueue.add(url = url, method="GET", countdown=countdown)

			newconfigs = datamodel.DBNewConfig().all().filter('user = ', userdb).fetch(1)
			if newconfigs:
				self.response.out.write('CONFIGUP\r\n')


			self.response.out.write('ANSWER: OK\r\n')
		else:
			self.response.out.write('ANSWER: USER_NOT_FOUND\r\n')

		#_log += "\n {DATABASE PUT() DISABLED}"
		logging.info(_log)

jit_lat = 0
jit_long = 0

def SaveGPSPointFromBin(pdata, result):
	global jit_lat
	global jit_long
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
	speed = (float(ord(pdata[15])) + float(ord(pdata[16])) / 100.0) * 1.852; # Переведем в км/ч

	if ord(pdata[13]) & 4:
		course = float(ord(pdata[17])*2 + 1) + float(ord(pdata[18])) / 100.0;
	else:
		course = float(ord(pdata[17])*2) + float(ord(pdata[18])) / 100.0;

	altitude = 100.0 * float(ord(pdata[19]) + ord(pdata[20])) / 10.0;

	error = False

	if latitude > 90.0: error = True
	if latitude < -90.0: error = True
	if longitude > 180.0: error = True
	if longitude < -180.0: error = True

	if SERVER_NAME=='localhost':
		#jit_lat = jit_lat + (random.random()-0.5)*0.001
		#jit_long = jit_long + (random.random()-0.5)*0.001
		#latitude = latitude + jit_lat
		#longitude = longitude + jit_long
		pass

	if error:
		logging.error("Corrupt latitude or longitude %f, %f" % (latitude, longitude))
		sstr = "  pdata: "
		for p in pdata:
			sstr += " %02X" % ord(p)
		sstr += "\nEncode partial data:\n\tdate:%s\n\tLatitude:%f\n\tLongitude:%f\n\tSatelites:%d\n\tSpeed:%f\n\tCource:%f\n\tAltitude:%f" % (datestamp, latitude, longitude, sats, speed, course, altitude)
		logging.error( sstr )
		return

	if sats < 3: return

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

	gpspoint = datamodel.DBGPSPoint()
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
					newbin = datamodel.DBGPSBin()
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
					point = SaveGPSPointFromBin(part, result)
					if point:
						points.append(point)
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
			futparts = datamodel.DBGPSBinParts().all().filter('user =', result.user).filter('dataid >=', result.dataid).fetch(10)
			for futpart in futparts:
				_log += '*'
				futpart.delete()

			if odata_s:
				_log += '\nFinding prevoiuse cut-part...'
				prevpart = datamodel.DBGPSBinParts().all().filter('user =', result.user).filter('dataid =', result.dataid-1).get()
				if prevpart:
					_log += 'ok. mergin...'
					part = prevpart.data + odata_s
					if len(part) == 23:
						_log += 'ok.'
						point = SaveGPSPointFromBin(part, result)
						if point:
							points.append(point)
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
				part2 = datamodel.DBGPSBinParts()
				part2.user = result.user
				part2.dataid = result.dataid
				part2.data = odata_f
				_log += '\nSaving cutting part.'
				part2.put()

			if len(points) > 0:
				db.put(points)		# Сохраним GPS-точки
			else:
				logging.error("points has no data")

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

class Map(TemplatedPage2):
	def get(self):
		#uimei = self.request.get('imei')

		#allusers = datamodel.DBUser.all().fetch(100)
		userdb = getUser(self.request)
		if userdb == None:
			userdb = self.account().users[0]
			pass

		template_values = {}
		template_values['map'] = True
		template_values['userdb'] = userdb
		#template_values['users'] = allusers
		#template_values['imei'] = uimei
		template_values['now'] = datetime.now()

		#path = os.path.join(os.path.dirname(__file__), 'map.html')
		#self.response.out.write(template.render(path, template_values))
		self.write_template(template_values)

class Map1(TemplatedPage2):
	def get(self):
		#uimei = self.request.get('imei')

		#allusers = datamodel.DBUser.all().fetch(100)
		userdb = getUser(self.request)
		#if userdb == None:
		#	userdb = self.account().users[0]
		#	pass

		template_values = {}
		template_values['map'] = True
		template_values['userdb'] = userdb
		template_values['now'] = datetime.now()

		#path = os.path.join(os.path.dirname(__file__), 'map.html')
		#self.response.out.write(template.render(path, template_values))
		self.write_template(template_values)

class Map2(TemplatedPage):
	def get(self):
		uimei = self.request.get('imei')

		#allusers = datamodel.DBUser.all().fetch(100)
		template_values = {}
		template_values['map'] = True
		#template_values['users'] = allusers
		template_values['imei'] = uimei
		template_values['now'] = datetime.now()

		#path = os.path.join(os.path.dirname(__file__), 'map.html')
		#self.response.out.write(template.render(path, template_values))
		self.write_template(template_values)

class RawData(webapp.RequestHandler):
	def get(self):
		print "RAW DATA"
		logging.info("DO RAW DATA")

"""
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
"""

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
		trect = datamodel.DBGPSPoint2()
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
		trect = datamodel.DBGPSPoint2()
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
					results = datamodel.DBGPSPoint2().all().fetch(int(cnt))
					for result in results:
						result.delete()
				elif batch:
					results = datamodel.DBGPSPoint2().all().fetch(int(batch))
					if results:
						db.delete(results)
				else:
					results = datamodel.DBGPSPoint2().all().fetch(1)
					if results:
						results[0].delete()

		values['runtime'] = profiler.time() * 1000
		values['answer'] = answer
		path = os.path.join(os.path.dirname(__file__), 'testdb.html')
		self.response.out.write(template.render(path, values))
		#self.redirect('testdb.html')


# обновление программного обеспечения
class Firmware(TemplatedPage):
	def get(self):
		user = users.get_current_user()
		username = ''
		if user:
			username = user.nickname()
		#
		cmd = self.request.get('cmd')
		fid = self.request.get('id')
		swid = self.request.get('swid')
		hwid = self.request.get('hwid')
		boot = self.request.get('boot')
		if boot:
			if boot == 'yes':
				boot = True
			else:
				boot = False
		else:
			boot = False

		#
		#login_url = users.create_login_url(self.request.uri)

		if cmd:
			if cmd == 'del':
				#if username == ADMIN_USERNAME:
				if users.is_current_user_admin():
					if fid:
						datamodel.DBFirmware().get_by_key_name(fid).delete()
				self.redirect("/firmware")

			elif cmd == 'check':	# Запросить версию самой свежей прошивки
				self.response.headers['Content-Type'] = 'application/octet-stream'	# Это единственный (пока) способ побороть Transfer-Encoding: chunked

				#fws = datamodel.DBFirmware().all().filter('hwid =', int(hwid, 16)).order('-swid').fetch(10)
				#for fw in fws:
				#	if fw.boot==False:
				#		self.response.out.write("SWID: %04X\r\n" % fw.swid)
				#		return
				#
				#self.response.out.write("NOT FOUND\r\n")
				#return
				#self.response.out.write("FIRMWARE\r\n")
						
				fw = datamodel.DBFirmware().all().filter('boot =', boot).filter('hwid =', int(hwid, 16)).order('-swid').fetch(1)
				if fw:
					self.response.out.write("SWID: %04X\r\n" % fw[0].swid)
				else:
					self.response.out.write("NOT FOUND\r\n")
				

			elif cmd == 'getbin':
				self.response.headers['Content-Type'] = 'application/octet-stream'
				if fid:
					fw = datamodel.DBFirmware().get_by_key_name(fid)
					fw = [fw]
				elif swid:
					fw = datamodel.DBFirmware().all().filter('boot =', boot).filter('hwid =', int(hwid, 16)).filter('swid =', int(swid, 16)).fetch(1)
				else:
					fw = datamodel.DBFirmware().all().filter('boot =', boot).filter('hwid =', int(hwid, 16)).order('-swid').fetch(1)
				if fw:
					self.response.out.write(fw[0].data)
				else:
					#self.response.headers['Content-Type'] = 'text/plain'
					self.response.out.write('NOT FOUND\r\n')

			elif cmd == 'get':
				if fid:
					fw = datamodel.DBFirmware().get_by_key_name(fid)
					fw = [fw]
				elif swid:
					fw = datamodel.DBFirmware().all().filter('boot =', boot).filter('hwid =', int(hwid, 16)).filter('swid =', int(swid, 16)).fetch(1)
				else:
					fw = datamodel.DBFirmware().all().filter('boot =', boot).filter('hwid =', int(hwid, 16)).order('-swid').fetch(1)
					#fws = datamodel.DBFirmware().all().filter('hwid =', int(hwid, 16)).order('-swid').fetch(10)
					#fw = None
					#for sfw in fws:
					#	if sfw.boot==False:
					#		fw = [sfw]
					#		break
				#self.response.headers['Content-Type'] = 'text/plain'
				self.response.headers['Content-Type'] = 'application/octet-stream'	# Это единственный (пока) способ побороть Transfer-Encoding: chunked
				if fw:
					#self.response.headers['Content-Type'] = 'application/octet-stream'
					#self.response.out.write(fw[0].data)
					by = 0
					line = 0
					#crc1 = 0
					crc2 = 0
					self.response.out.write("SWID:%04X" % fw[0].swid)
					self.response.out.write("\r\nLENGTH:%04X" % len(fw[0].data))
					#cuting = 0

					#config2 = ord(fw[0].data[24]) + ord(fw[0].data[25])*256
					#config1 = ord(fw[0].data[26]) + ord(fw[0].data[27])*256
					#self.response.out.write("\r\nCONFIG2:%04X" % config2)
					#self.response.out.write("\r\nCONFIG1:%04X" % config1)

					for byte in fw[0].data:
						if by == 0:
							self.response.out.write("\r\nLINE%04X:" % line)
							line = line + 1
							by = 32
							#cuting = cuting + 1
							#if cuting == 230: break
						self.response.out.write("%02X" % ord(byte))
						#crc = crc^ord(byte)
						#crc1 = updcrc1(crc1, ord(byte))
						crc2 = utils.crc(crc2, ord(byte))
						by = by - 1
					#self.response.out.write("\r\nCRC%04X\r\nENDDATA\r\n" % updcrc(0, fw[0].data))
					self.response.out.write("\r\n")
					#self.response.out.write("CRC:%04X\r\n" % crc1)
					self.response.out.write("CRC:%04X\r\n" % crc2)
					self.response.out.write("ENDDATA\r\n")
				else:
					self.response.out.write('NOT FOUND\r\n')

			elif cmd == 'patch':
				fws = datamodel.DBFirmware().all().fetch(500)
				for fw in fws:
					if fw.boot:
						pass
					else:
						fw.boot = False
						fw.put()
				self.redirect("/firmware")
			else:
				self.redirect("/firmware")
		else:
			#template_values = ckechUser(self.request.uri, self.response)
			#if not template_values:
			#	return
			template_values = {}

			if hwid:
				firmwares = datamodel.DBFirmware().all().filter('boot =', boot).filter('hwid =', int(hwid, 16)).fetch(100)
			else:
				firmwares = datamodel.DBFirmware().all().filter('boot =', boot).fetch(100)
			nfw = []
			for fw in firmwares:
				#fw.ofwid = "%X" % fw.hwid
				#fw.oswid = "%X" % fw.swid
				nfw.append({
					'key': fw.key().name(),
					'hwid': "%04X" % fw.hwid,
					'swid': "%04X" % fw.swid,
					'cdate': fw.cdate,
					'size': fw.size,
					'desc': fw.desc,
				})
			template_values['firmwares'] = nfw
			#path = os.path.join(os.path.dirname(__file__), 'firmware.html')
			#self.response.out.write(template.render(path, template_values))
			self.write_template(template_values)


	def post(self):
		self.response.headers['Content-Type'] = 'text/plain'

		boot = self.request.get('boot')

		pdata = self.request.body
		hwid = int(self.request.get('hwid'), 16)
		swid = int(self.request.get('swid'), 16)

		if boot:
			newfw = datamodel.DBFirmware(key_name = "FWBOOT%04X" % hwid)
			newfw.desc = u"Загрузчик"
			newfw.boot = True
		else:
			newfw = datamodel.DBFirmware(key_name = "FWGPS%04X%04X" % (hwid, swid))
			newfw.desc = u"Образ ядра"
		newfw.hwid = hwid
		newfw.swid = swid
		newfw.data = pdata
		newfw.size = len(pdata)
		newfw.put()

		self.response.out.write("ROM ADDED: %d\r\n" % len(pdata))

#class myWSGIApplication(webapp.WSGIApplication):
#	def __call__(self, environ, start_response):
#		webapp.WSGIApplication.__call__(self, environ, my_start_response)
#		return ['']

#application = myWSGIApplication(

class SetDescription(webapp.RequestHandler):
	def get(self):
		callback = self.request.get('callback')
		name = self.request.get('name')
		value = self.request.get('value')


		newdescr = datamodel.DBDescription(key_name = "DESC%s" % name)
		newdescr.name = name
		newdescr.value = value
		newdescr.put()

		self.response.headers['Content-Type']   = 'text/javascript; charset=utf-8'
		jsonresp = {
			"responseData": {
				"confirm": 1,
			}
		}
		nejson = json.dumps(jsonresp)
		self.response.out.write(callback + "(" + nejson + ")\r")

class SetUserDescription(webapp.RequestHandler):
	def get(self):
		callback = self.request.get('callback')
		uimei = self.request.get('imei')
		value = self.request.get('value')

		self.response.headers['Content-Type']   = 'text/javascript; charset=utf-8'

		userdb = datamodel.DBUser().all().filter('imei =', uimei).fetch(1)
		if userdb:
			userdb[0].desc = value
			userdb[0].put()

			jsonresp = {"responseData": {"confirm": 1}}
		else:
			jsonresp = {"responseData": {"confirm": 0}}

		nejson = json.dumps(jsonresp)
		self.response.out.write(callback + "(" + nejson + ")\r")


class Svg1(TemplatedPage):
	def get(self):
		uimei = self.request.get('imei')

		template_values = {}
		template_values['imei'] = uimei
		#self.write_template(template_values)
		self.response.headers['Content-Type']   = 'text/html'
		path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.html')
		self.response.out.write(template.render(path, template_values))

class Svg3(TemplatedPage):
	def get(self):
		uimei = self.request.get('imei')

		template_values = {}
		template_values['imei'] = uimei
		#self.write_template(template_values)
		self.response.headers['Content-Type']   = 'text/html'
		path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.html')
		self.response.out.write(template.render(path, template_values))

class Svg2(TemplatedPage):
	def get(self):
		uimei = self.request.get('imei')

		template_values = {}
		template_values['imei'] = uimei
		#self.write_template(template_values)
		self.response.headers['Content-Type']   = 'text/xml'
		path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.xml')
		self.response.out.write(template.render(path, template_values))


class BinBackup(TemplatedPage):
	def get(self):
		uimei = self.request.get('imei')
		userdb = getUser(self.request)

		cmd = self.request.get('cmd')
		total = 0
		if cmd:
			ukey = self.request.get('key')
			if cmd == 'getbin':
				self.response.headers['Content-Type'] = 'application/octet-stream'
				#bindata = datastore.Get(datastore.Key(ukey))
				bindata = db.get(db.Key(ukey))
				pdata = bindata.data
				if ((len(pdata)-2) & 31) != 0:
					while (len(pdata) & 31)!=0:
						pdata += chr(0)
				if (len(pdata) & 31)==0:
					crc = 0
					for byte in pdata:
						crc = utils.crc(crc, ord(byte))
					pdata += chr(crc & 0xFF)
					pdata += chr((crc>>8) & 0xFF)

				self.response.out.write(pdata)
				return
			elif cmd == 'fixcrc':
				bindata = db.get(db.Key(ukey))
				pdata = bindata.data
				if ((len(pdata)-2) & 31) != 0:
					while (len(pdata) & 31)!=0: pdata += chr(0)
				if (len(pdata) & 31)==0:
					crc = 0
					for byte in pdata:
						crc = utils.crc(crc, ord(byte))
					pdata += chr(crc & 0xFF)
					pdata += chr((crc>>8) & 0xFF)
					bindata.data = pdata
					bindata.put()
				self.redirect("/binbackup?imei=%s" % uimei)
				return
			elif cmd == 'fixlen':
				bindata = db.get(db.Key(ukey))
				pdata = bindata.data
				while (len(pdata) & 31)!=0: pdata += chr(0)
					
				crc = 0
				for byte in pdata:
					crc = utils.crc(crc, ord(byte))
				pdata += chr(crc & 0xFF)
				pdata += chr((crc>>8) & 0xFF)
				bindata.data = pdata
				bindata.put()
				self.redirect("/binbackup?imei=%s" % uimei)
				return
			elif cmd == 'del':
				db.delete(db.Key(ukey))
				self.redirect("/binbackup?imei=%s" % uimei)
				return
			elif cmd == 'delall':
				dbbindata = datamodel.DBGPSBinBackup.all().filter('user =', userdb).order('cdate').fetch(500)
				#for bindata in dbbindata:
				#	bindata.delete()
				if dbbindata:
					db.delete(dbbindata)
				self.redirect("/binbackup?imei=%s" % uimei)
				return
			elif cmd == 'pack':
				self.response.headers['Content-Type'] = 'application/octet-stream'
				pdata = ''
				cfilter = self.request.get('filter')
				cnt = self.request.get('cnt')
				count = 200
				if cnt: count = int(cnt)
				today = date.today()
				logging.info("Today: %s" % today)

				#dbbindata = datamodel.DBGPSBinBackup.all().filter('user =', userdb).order('-cdate').fetch(count)
				if cfilter:
					dbbindata = userdb.gpsbackups.filter('cdate >=', today).order('-cdate').fetch(count)
				else:
					dbbindata = userdb.gpsbackups.order('-cdate').fetch(count)
				for bindata in dbbindata:
					npdata = bindata.data
					#bindata.datasize = len(npdata)
					if npdata[0] == 'P':	# POST-bug
						continue

					if (len(npdata) & 31)==0:
						pdata += npdata
					else:
						if ((len(npdata)-2) & 31) == 0:
							pdata += npdata[:-2]
						else:
							while (len(npdata) & 31)!=0: npdata += chr(0)
							pdata += npdata


				crc = 0
				for byte in pdata:
					crc = utils.crc(crc, ord(byte))
				pdata += chr(crc & 0xFF)
				pdata += chr((crc>>8) & 0xFF)
				"""
				crc = ord(pdata[-1])*256 + ord(pdata[-2])
				pdata = pdata[:-2]
				_log += '\n==\tData size: %d' % len(pdata)

				"""
				self.response.out.write(pdata)
				return

		if userdb:
			dbbindata = datamodel.DBGPSBinBackup.all().filter('user =', userdb).order('-cdate').fetch(200)

			for bindata in dbbindata:
				bindata.datasize = len(bindata.data)
				if (bindata.datasize & 31)==0:
					bindata.needfix = True
					bindata.wronglen = False
					total += bindata.datasize
				else:
					bindata.needfix = False
					total += bindata.datasize - 2

					if ((bindata.datasize-2) & 31)!=0:
						bindata.wronglen = True
					else:
						bindata.wronglen = False

				if bindata.data[0] == 'P':
					bindata.postbug = True
				else:
					bindata.postbug = False

				bindata.sdate = fromUTC(bindata.cdate)	#.strftime("%d/%m/%Y %H:%M:%S")
			total += 2
			allusers = None
		else:
			dbbindata = None
			allusers = datamodel.DBUser.all().fetch(100)


		#template_values = {}
		#template_values['imei'] = uimei
		#template_values['dbbindata'] = dbbindata

		self.response.headers['Content-Type']   = 'text/html'
		#path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.html')
		#self.response.out.write(template.render(path, template_values))
		self.write_template({
			'imei': uimei,
			'dbbindata': dbbindata,
			'total': total,
			'userdb': userdb,
			'allusers': allusers
		})

class GpsTestBin(webapp.RequestHandler):
	def get(self):
		log = "\n=== === == GpsTestBin:\n"
		uimei = self.request.get('imei')
		pdata = self.request.body
		log += "    IMEI: %s\n" % uimei
		log += "    DATASIZE: %d\n" % len(pdata)
		logging.info(log)
		self.response.headers['Content-Type']   = 'text/plain'
		self.response.out.write("OK")


application = webapp.WSGIApplication(
	[('/', MainPage),
	#('/regid', RegId),
	('/gpstestbin.*', GpsTestBin),
	('/sign', Guestbook),
	('/addlog', AddLog),
	('/users.*', UsersList),
	('/delUser.*', DelUser),
	('/logs2.*', ViewLogs2),
	('/logs.*', ViewLogs),
	('/jsonlogs.*', JsonLogs),
	('/dellogs.*', DelLogs),
	('/delgeos.*', DelGeos),
	('/del1geos.*', Del1Geos),
	('/lastpos.*', LastPos),
	('/geosjson', GeosJSON),
	('/geos2.*', Geos2),
	('/geos.*', Geos),
	('/stylesheets.*', CSSfiles),
	('/config.*', Config),
	('/params.*', Params),
	('/help.*', Help),
	('/testbin.*', TestBin),
	('/bingeos.*', BinGeos),
	('/parsebingeos.*', ParseBinGeos),
	('/getbin.*', GetBinGeos),
	('/map1.*', Map1),
	('/map.*', Map),
	('/raw', RawData),
	('/testdb.*', TestDB),
	('/system.*', System),
	('/firmware.*', Firmware),
	('/setdescr.*', SetDescription),
	('/setuserdescr.*', SetUserDescription),
	('/gettrack.*', GetTrack),
	('/svg1.*', Svg1),
	('/svg2.*', Svg2),
	('/svg3.*', Svg3),
	('/binbackup.*', BinBackup),
	],
	debug=True
)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
