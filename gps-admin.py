# -*- coding: utf-8 -*-
#import cgi
#from google.appengine.tools.dev_appserver import datastore
import logging
import os
#import zlib
#import math
import utils

#from datetime import date
#from datetime import datetime
from datetime import date, timedelta, datetime

#from django.utils import simplejson as json
from google.appengine.api import users
from google.appengine.api import datastore
#from google.appengine.api import urlfetch
#from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
#from google.appengine.tools import bulkloader

# Must set this env var *before* importing any part of Django.
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
#TIME_ZONE = 'America/Los_Angeles'  # i.e., Mountain View
from google.appengine.ext.webapp import template

#import models
import datamodel

#ADMIN_USERNAME = 'baden.i.ua'

SERVER_NAME = os.environ['SERVER_NAME']

OLDDATA = timedelta(days=24)

def checkUser(uri, response):
	user = users.get_current_user()

	if user:
		#url = users.create_logout_url(self.request.uri)
		login_url = users.create_login_url(uri)
		username = user.nickname()
	else:
		#response.out.write(u"<html><!--html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\"--><body>")
		#response.out.write(u"Для работы с системой необходимо выполнить вход под своим Google-аккаунтом.<br>")
		#response.out.write(u"Нажмите <a href=" + users.create_login_url(uri) + ">[ выполнить вход ]</a> для того чтобы перейти на сайт Google для ввода логина/пароля.<br>")
		#response.out.write(u"После ввода логина/пароля вы будете возврыщены на сайт системы.")
		#response.out.write(u"</body></html>")
		self.redirect(users.create_login_url(self.request.uri))
		return False
	return {
		'login_url': login_url,
		'username': username,
		#'admin': username == ADMIN_USERNAME,
		'admin': users.is_current_user_admin(),
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
			#values['admin'] = (username == ADMIN_USERNAME)
			values['admin'] = users.is_current_user_admin()
			values['server_name'] = SERVER_NAME

			data = '313233343536373839'
			crc = 0
			for byte in data: crc = utils.crc(crc, ord(byte))
			values['crc'] = "0x%04X" % crc

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

class AdminPage(TemplatedPage):
	def get(self):
		accounts = datamodel.DBAccounts().all()

		template_values = {'accounts': accounts}
		#template_values['now'] = datetime.now()
		self.write_template(template_values)

class AdminClosure(TemplatedPage):
	def get(self):
		accounts = datamodel.DBAccounts().all()

		template_values = {'accounts': accounts}
		#template_values['now'] = datetime.now()
		self.write_template(template_values)

class AdminData(TemplatedPage):
	def get(self):
		accounts = datamodel.DBAccounts().all()

		geologs = datamodel.DBGPSPoint.all().order('date').fetch(1)
		if geologs:
			lastlog = geologs[0]
		else:
			lastlog = None
			
		now = datetime.now()
		geologs_count = datamodel.DBGPSPoint.all(keys_only=True).filter("date <", datetime.now() - OLDDATA).order('date').count(5000)
		#q = userdb.geos.order('-date')

		template_values = {'accounts': accounts}
		template_values['lastlog'] = lastlog
		template_values['oldcnt'] = geologs_count
		self.write_template(template_values)

class AdminFlushOld(webapp.RequestHandler):
	def get(self):
		db.delete(datamodel.DBGPSPoint.all(keys_only=True).filter("date <", datetime.now() - OLDDATA).order('date').fetch(100))
		#self.redirect('/admin.data')

class AdminFlushOld2(webapp.RequestHandler):
	def get(self):
		db.delete(datamodel.DBGPSBinBackup.all(keys_only=True).filter("cdate <=", datetime.now() - OLDDATA).order('cdate').fetch(500))
		#self.redirect('/admin.data')

application = webapp.WSGIApplication(
	[
	('/admin', AdminPage),
	('/admin.data', AdminData),
	('/admin.flushold', AdminFlushOld),
	('/admin.flushold2', AdminFlushOld2),
	('/admin.closure', AdminClosure),
	],
	debug=True
)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
