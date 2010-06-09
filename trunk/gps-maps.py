# -*- coding: utf-8 -*-
#import cgi
#from google.appengine.tools.dev_appserver import datastore
import logging
import os
import zlib
import math

from datetime import date
from datetime import datetime
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

from google.appengine.ext.webapp import template

#import models
import datamodel

ADMIN_USERNAME = 'baden.i.ua'


# 16-bit CRCs should detect 65535/65536 or 99.998% of all errors in
# data blocks up to 4096 bytes
"""
MASK_CCITT = 0x1021 # CRC-CCITT mask (ISO 3309, used in X25, HDLC)
MASK_CRC16 = 0xA001 # CRC16 mask (used in ARC files)

#----------------------------------------------------------------------------
# Calculate and return an incremental CRC value based on the current value
# and the data bytes passed in as a string.
#
def updcrc1(crc, data, mask=MASK_CCITT):

	# data_length = len(data)
	# unpackFormat = '%db' % data_length
	# unpackedData = struct.unpack(unpackFormat, data)

	c = data
	c = c << 8

	for j in xrange(8):
		if (crc ^ c) & 0x8000:
			crc = (crc << 1) ^ mask
		else:
			crc = crc << 1
		c = c << 1

	return crc & 0xffff
"""
""" CRC16-CCITT hash, part of Battlefield 2142 Auth token maker
This is the python module package for computing CRC16-CCITT hash.
"""

CRC16_CCITT_table = (
        0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7, 0x8108, 0x9129, 0xa14a, 0xb16b,
        0xc18c, 0xd1ad, 0xe1ce, 0xf1ef, 0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
        0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de, 0x2462, 0x3443, 0x0420, 0x1401,
        0x64e6, 0x74c7, 0x44a4, 0x5485, 0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
        0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4, 0xb75b, 0xa77a, 0x9719, 0x8738,
        0xf7df, 0xe7fe, 0xd79d, 0xc7bc, 0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
        0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b, 0x5af5, 0x4ad4, 0x7ab7, 0x6a96,
        0x1a71, 0x0a50, 0x3a33, 0x2a12, 0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
        0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41, 0xedae, 0xfd8f, 0xcdec, 0xddcd,
        0xad2a, 0xbd0b, 0x8d68, 0x9d49, 0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
        0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78, 0x9188, 0x81a9, 0xb1ca, 0xa1eb,
        0xd10c, 0xc12d, 0xf14e, 0xe16f, 0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
        0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e, 0x02b1, 0x1290, 0x22f3, 0x32d2,
        0x4235, 0x5214, 0x6277, 0x7256, 0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
        0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405, 0xa7db, 0xb7fa, 0x8799, 0x97b8,
        0xe75f, 0xf77e, 0xc71d, 0xd73c, 0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
        0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab, 0x5844, 0x4865, 0x7806, 0x6827,
        0x18c0, 0x08e1, 0x3882, 0x28a3, 0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
        0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92, 0xfd2e, 0xed0f, 0xdd6c, 0xcd4d,
        0xbdaa, 0xad8b, 0x9de8, 0x8dc9, 0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
        0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8, 0x6e17, 0x7e36, 0x4e55, 0x5e74,
        0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
        )

def updcrc2(crc, data):
    """ Compute correct enough :grin: CRC16 CCITT for using in BF2142 auth token """
    return (((crc << 8) & 0xff00) ^ CRC16_CCITT_table[((crc >> 8) ^ (0xff & data))])

def checkUser(uri, response):
	user = users.get_current_user()

	if user:
		#url = users.create_logout_url(self.request.uri)
		login_url = users.create_login_url(uri)
		username = user.nickname()
	else:
		response.out.write("<html><body>")
		response.out.write("Для работы с системой необходимо выполнить вход под своим Google-аккаунтом.<br>")
		response.out.write("Нажмите <a href=" + users.create_login_url(uri) + ">[ выполнить вход ]</a> для того чтобы перейти на сайт Google для ввода логина/пароля.<br>")
		response.out.write("После ввода логина/пароля вы будете возврыщены на сайт системы.")
		response.out.write("</body></html>")
		#self.redirect(users.create_login_url(self.request.uri))
		return False
	return {
		'login_url': login_url,
		'username': username,
		'admin': username == ADMIN_USERNAME,
	}

class TemplatedPage(webapp.RequestHandler):
	def write_template(self, values):

		user = users.get_current_user()

		if user:
			#url = users.create_logout_url(self.request.uri)
			login_url = users.create_login_url(self.request.uri)
			username = user.nickname()
			values['login_url'] = login_url
			values['username'] = username
			values['admin'] = (username == ADMIN_USERNAME)

			path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.html')
			self.response.out.write(template.render(path, values))
		else:
			self.response.out.write("<html><body>")
			self.response.out.write("Для работы с системой необходимо выполнить вход под своим Google-аккаунтом.<br>")
			self.response.out.write("Нажмите <a href=" + users.create_login_url(self.request.uri) + ">[ выполнить вход ]</a> для того чтобы перейти на сайт Google для ввода логина/пароля.<br>")
			self.response.out.write("После ввода логина/пароля вы будете возврыщены на сайт системы.")
			self.response.out.write("</body></html>")
			#self.redirect(users.create_login_url(self.request.uri))

class MainPage(TemplatedPage):
	def get(self):
		template_values = {}
		template_values['now'] = datetime.now()

		crc = 0
		crc = updcrc2(crc, ord('0'))
		crc = updcrc2(crc, ord('0'))
		crc = updcrc2(crc, ord('0'))

		template_values['crc1'] = "0x%04X" % crc

		#logging.warning("Test warning logging.");
		#logging.error("Test error logging.");
		#logging.debug("Test debug logging.");
		#logging.info("Test info logging.");
		#logging.critical("Test critical logging.");

		#path = os.path.join(os.path.dirname(__file__), 'index.html')
		#self.response.out.write(template.render(path, template_values))
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

def getUser(request):
	uimei = request.get('imei')
	logging.debug(uimei)
#	ukey = request.get('ukey')
#	uid = request.get('uid')
#	if uid:
#		userdb = DBUser().get_by_id(long(uid))
		#self.response.out.write('Get by id (%d)\r\n' % userid)
	if uimei:
		userdbq = datamodel.DBUser().all().filter('imei =', uimei).fetch(1)
		#userdbq = datamodel.DBUser().all().filter('imei =', uimei).get()
		if userdbq:
			userdb = userdbq[0] 
			#self.response.out.write('Get by imei (%s)\r\n' % uimei)
		else:
			userdb = None
			#self.response.out.write('User not found by imei (%s)\r\n' % uimei)
	else:
		userdb = None

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

		if userdb:
			gpslog = datamodel.GPSLogs()
			gpslog.user = userdb
			gpslog.text = text
			gpslog.put()
			self.response.out.write('Add log for user (phone:%s IMEI:%s).\r\n' % (userdb.phone, userdb.imei))

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
	def post(self):
		userid = int(self.request.get('id'))
		self.response.out.write('Request body (%s)<br>' % self.request.body)
		file = self.request.get('file')
		self.response.out.write('File: %s' % file)

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

MAXLOGS = 20

class ViewLogs(TemplatedPage):
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
			gpslogs = datamodel.GPSLogs.all().filter('date <=', datetime.strptime(datemark, "%Y%m%d%H%M%S%f")).order('-date').fetch(MAXLOGS+1)
			#urlprev = '<a href="logs?date=%s">Prev</a> %s ' % (gpslogs[0].date.strftime("%d-%m-%y %H:%M:%S.%f"), datemark)  
		else:
			gpslogs = datamodel.GPSLogs.all().order('-date').fetch(MAXLOGS+1)
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

		template_values = {}
		template_values['gpslogs'] = gpslogs
		template_values['urlnext'] = urlnext
		template_values['urlprev'] = urlprev

		#path = os.path.join(os.path.dirname(__file__), 'logs.html')
		#self.response.out.write(template.render(path, template_values))
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

class DelUser(webapp.RequestHandler):
	def get(self):
		ukey = self.request.get('key')
		uid = self.request.get('id')
		#duser = datamodel.DBUser().get_by_key_name(cls, key_names, parent)
		if ukey:
			datastore.Delete(datastore.Key(ukey))

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

class Geos(TemplatedPage):
	def get(self):

		geologs = datamodel.DBGPSPoint.all().order('-date').fetch(MAXLOGS+1)
		#geologs = datamodel.DBGPSPoint.all().order('-date').fetch(100)
		for geolog in geologs:
			try:
				uuser = geolog.user
				geolog.imei = uuser.imei 
			except:
				geolog.imei = 'deleted' 
			geolog.sdate = geolog.cdate.strftime("%d/%m/%Y %H:%M") 

		#path = os.path.join(os.path.dirname(__file__), 'geos.html')
		#self.response.out.write(template.render(path, template_values))
		self.write_template({'geologs': geologs})

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
		start_time = datetime.now()
		logging.info("GeosJSON start (%s)" % start_time.strftime("%H:%M:%S"))

		userdb = getUser(self.request)

		if userdb == None:
			logging.info("User not found.")
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
				geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).filter('date >=', datefrom).order('date').fetch(int(first))
			else:
				geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).order('date').fetch(int(first))
				pass
		else:
			last = self.request.get('last')
			if last:
				logging.info("GeosJSON last: %s" % last)
				geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).filter('date <=', dateto).order('-date').fetch(int(last))
			else:
				geologs = datamodel.DBGPSPoint.all().filter('user =', userdb).filter('date >=', datefrom).filter('date <=', dateto).order('-date').fetch(500)

		#self.response.out.write("// User imei: %s\r// Date from: %s\r// Date to: %s\r" % (userdb.imei, datefrom, dateto))

#.filter('date <=', datetime.strptime(datemark, "%Y%m%d%H%M%S%f"))
		#geologs = DBGPSPoint.all().order('-date').filter('user =', userdb)
		#geologs = DBGPSPoint.all().order('-date').fetch(500)
		#geologs = DBGPSPoint.all().order('-date').fetch(MAXLOGS+1)

		optim = self.request.get('optim')

		dif_time = datetime.now() - start_time
		logging.info("GeosJSON db ready (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))

		results = []
		if geologs:
			if not first:
				dif_time = datetime.now() - start_time
				logging.info("Start reverse (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))
				geologs.reverse()
				logging.info("Stop reverse (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))

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
			#if first:
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

		dif_time = datetime.now() - start_time
		logging.info("GeosJSON response ready (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))


		nejson = json.dumps(jsonresp)
		self.response.out.write(callback + "(" + nejson + ")\r")

		dif_time = datetime.now() - start_time
		logging.info("GeosJSON json-out ready (+%.4fsec)" % (dif_time.seconds + float(dif_time.microseconds)/1000000.0))

		logging.info("GeosJSON data: %d values" % len(results))

		return

class DelGeos(webapp.RequestHandler):
	def get(self):
		geologs = datamodel.DBGPSPoint.all().order('-date').fetch(500)
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

		userdb = getUser(self.request)
		#logging.debug(userdb.imei)

		if userdb == None:
			allusers = datamodel.DBUser.all().fetch(100)
			template_values = {'now': datetime.now(),
			    'users':allusers
			}

			path = os.path.join(os.path.dirname(__file__), 'templates/config.html')
			self.response.out.write(template.render(path, template_values))

		else:
			if cmd == 'last':
				#self.response.out.write('<html><head><link type="text/css" rel="stylesheet" href="stylesheets/main.css" /></head><body>CONFIG:<br><table>')
				#self.response.out.write(u"<tr><th>Имя</th><th>Тип</th><th>Значение</th><th>Заводская установка</th></tr>" )

				descriptions = datamodel.DBDescription().all() #.fetch(500)
				descs={}
				for description in descriptions:
					descs[description.name] = description.value
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


					for config, value in configs.items():
						desc = u"Нет описания"
						if config in descs:
							desc = descs[config]

						if config in waitconfig:
							configs[config] = (configs[config][0], configs[config][1], configs[config][2], waitconfig[config], desc)
						else:
							configs[config] = (configs[config][0], configs[config][1], configs[config][2], None, desc)
							#configs[config] = (configs[config][0], configs[config][1], configs[config][2], configs[config][1])

					# Для удобства отсортируем словарь в список
					#sconfigs = sortDict(configs)
					sconfigs = [(key, configs[key]) for key in sorted(configs.keys())]

					template_values = {
					    'configs': sconfigs,
					    'user': userdb,
					    'imei': uimei
					}

					path = os.path.join(os.path.dirname(__file__), 'templates/config-last.html')
					self.response.out.write(template.render(path, template_values))
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
		userdb = getUser(self.request)
		if not userdb:
			self.response.out.write("NO USER")
			return

		cmd = self.request.get('cmd')
		if cmd == 'save':
			self.response.headers['Content-Type'] = 'text/plain'	#minimizing data
			newconfigs = datamodel.DBConfig().all().filter('user = ', userdb).fetch(1)
			if newconfigs:
				newconfig = newconfigs[0]
				config = eval(zlib.decompress(newconfig.config))
				#config = eval(newconfig.strconfig)
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

	error = False

	if latitude > 90.0: error = True
	if latitude < -90.0: error = True
	if longitude > 180.0: error = True
	if longitude < -180.0: error = True

	if error:
		logging.error("Corrupt latitude or longitude %f, %f" % (latitude, longitude))
		sstr = "  pdata: "
		for p in pdata:
			sstr += " %02X" % ord(p)
		logging.error( sstr )
		return

	sats = ord(pdata[14])
	if sats < 3: return

	fix = 1
	speed = float(ord(pdata[15])) + float(ord(pdata[16])) / 100.0;

	if ord(pdata[13]) & 4:
		course = float(ord(pdata[17])*2 + 1) + float(ord(pdata[18])) / 100.0;
	else:
		course = float(ord(pdata[17])*2) + float(ord(pdata[18])) / 100.0;

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
				part2 = datamodel.DBGPSBinParts()
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

class Map(TemplatedPage):
	def get(self):
		uimei = self.request.get('imei')

		allusers = datamodel.DBUser.all().fetch(100)
		template_values = {}
		template_values['map'] = True
		template_values['users'] = allusers
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
class Firmware(webapp.RequestHandler):

	def get(self):
		user = users.get_current_user()
		username = ''
		if user:
			username = user.nickname()

		cmd = self.request.get('cmd')
		hwid = self.request.get('hwid')

		login_url = users.create_login_url(self.request.uri)

		if cmd:
			if cmd == 'del':
				if self.username == ADMIN_USERNAME:
					fid = self.request.get('id')
					if fid:
						datamodel.DBFirmware().get_by_key_name(fid).delete()
				self.redirect("/firmware")

			elif cmd == 'check':	# Запросить версию самой свежей прошивки
				fw = datamodel.DBFirmware().all().filter('hwid =', int(hwid, 16)).order('-swid').fetch(1)
				resp = ""	# Боремся с Transfer-Encoding: chunked
				#self.response.headers['Content-Type'] = 'text/plain'
				self.response.headers['Content-Type'] = 'application/octet-stream'	# Это единственный (пока) способ побороть Transfer-Encoding: chunked
				#self.response.headers['Content-Length'] = len(resp)
				#self.response.headers['Transfer-Encoding'] = 'gzip'
				#self.response.headers['Transfer-Encoding'] = 'identity'
				if fw:
					#self.response.out.write("a\r\nSWID: %04X" % fw[0].swid)
					resp = "SWID: %04X\r\n" % fw[0].swid
				else:
					#self.response.out.write("NOT FOUND")
					resp = "NOT FOUND\r\n"
				self.response.out.write(resp)


			elif cmd == 'getbin':
				swid = self.request.get('swid')
				if swid:
					fw = datamodel.DBFirmware().all().filter('hwid =', int(hwid, 16)).filter('swid =', int(swid, 16)).fetch(1)
				else:
					fw = datamodel.DBFirmware().all().filter('hwid =', int(hwid, 16)).order('-swid').fetch(1)
				if fw:
					self.response.headers['Content-Type'] = 'application/octet-stream'
					self.response.out.write(fw[0].data)
				else:
					#self.response.headers['Content-Type'] = 'text/plain'
					self.response.headers['Content-Type'] = 'application/octet-stream'	# Это единственный (пока) способ побороть Transfer-Encoding: chunked
					self.response.out.write('NOT FOUND\r\n')

			elif cmd == 'get':
				swid = self.request.get('swid')
				if swid:
					fw = datamodel.DBFirmware().all().filter('hwid =', int(hwid, 16)).filter('swid =', int(swid, 16)).fetch(1)
				else:
					fw = datamodel.DBFirmware().all().filter('hwid =', int(hwid, 16)).order('-swid').fetch(1)
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
						crc2 = updcrc2(crc2, ord(byte))
						by = by - 1
					#self.response.out.write("\r\nCRC%04X\r\nENDDATA\r\n" % updcrc(0, fw[0].data))
					self.response.out.write("\r\n")
					#self.response.out.write("CRC:%04X\r\n" % crc1)
					self.response.out.write("CRC:%04X\r\n" % crc2)
					self.response.out.write("ENDDATA\r\n")
				else:
					self.response.out.write('NOT FOUND\r\n')

			else:
				self.redirect("/firmware")
		else:
			template_values = ckechUser(self.request.uri, self.response)
			if not template_values:
				return

			if hwid:
				firmwares = datamodel.DBFirmware().all().filter('hwid =', int(hwid, 16)).fetch(100)
			else:
				firmwares = datamodel.DBFirmware().all().fetch(100)
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
			path = os.path.join(os.path.dirname(__file__), 'firmware.html')
			self.response.out.write(template.render(path, template_values))

	def post(self):
		self.response.headers['Content-Type'] = 'text/plain'

		pdata = self.request.body
		hwid = int(self.request.get('hwid'), 16)
		swid = int(self.request.get('swid'), 16)

		newfw = datamodel.DBFirmware(key_name = "FWGPS%04X%04X" % (hwid, swid))
		newfw.hwid = hwid
		newfw.swid = swid
		newfw.data = pdata
		newfw.size = len(pdata)
		newfw.desc = u"Нет описания"
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
	('/params.*', Params),
	('/help.*', Help),
	('/testbin.*', TestBin),
	('/bingeos.*', BinGeos),
	('/parsebingeos.*', ParseBinGeos),
	('/getbin.*', GetBinGeos),
	('/map.*', Map),
	('/raw', RawData),
	('/testdb.*', TestDB),
	('/system.*', System),
	('/firmware.*', Firmware),
	('/setdescr.*', SetDescription),
	],
	debug=True
)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
