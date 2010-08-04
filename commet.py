# -*- coding: utf-8 -*-
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from django.utils import simplejson as json
from google.appengine.api import memcache
#from google.appengine.api import datastore
from google.appengine.api import channel

key = "ABCD"

class MainPage(webapp.RequestHandler):
	global key
	def get(self):
		id = channel.create_channel(key)
		self.response.out.write({'channel_id': id})


class Commet(webapp.RequestHandler):
	global key
	def get(self):
		id = channel.create_channel(key)
		values = {'channel_id': id}
		path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.html')
		self.response.out.write(template.render(path, values))


class CommetMsg(webapp.RequestHandler):
	global key
	def get(self):
		# something happened!
		channel.send_message(key, 'Hello, world!!!')

application = webapp.WSGIApplication([
	('/commet-msg.*', CommetMsg),
	('/commet.*', Commet),
	],
	debug=True
)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
