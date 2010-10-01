# -*- coding: utf-8 -*-

import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


class Benchmark(webapp.RequestHandler):
	def get(self):
		values = {}
		path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.html')
		#self.response.headers['Content-Type']   = 'text/xml'
		self.response.out.write(template.render(path, values))


class PutData(webapp.RequestHandler):
	def get(self):
		logging.info("   ===> Bencmark: put-data")
		self.redirect("/benchmark")

application = webapp.WSGIApplication(
	[
		('/benchmark/put-data.*', PutData),
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
