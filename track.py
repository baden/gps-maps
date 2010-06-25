# -*- coding: utf-8 -*-
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from django.utils import simplejson as json
from google.appengine.api import memcache
#from google.appengine.api import datastore

class Track(webapp.RequestHandler):
	def get(self):
		values = {}
		path = os.path.join(os.path.dirname(__file__), 'templates', self.__class__.__name__ + '.html')
		self.response.out.write(template.render(path, values))
		#По русски
		#self.response.headers['Content-Type'] = 'text/plain'
		#self.response.out.write("Hello")

class TrackJS(webapp.RequestHandler):
	def get(self):
		#По русски
		self.response.headers['Content-Type'] = 'text/javascript; charset=utf-8'
		#self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write(
			"""
// Hello
postMessage("Работаю...");
var counter = 0;
function update() {
	counter++;
	postMessage(counter);
	timer = setTimeout(update, 1000);
}
update();
			"""
		)

#counter = 1

def get_counter():
	counter = memcache.get("counter")
	if counter is not None:
		return counter
	else:
		counter = 1
		memcache.add("counter", counter, 10)
		return counter

def incr_counter():
	#counter = counter + 1
	memcache.incr("counter")

class TrackCounter(webapp.RequestHandler):
	def get(self):
#		global counter
		#По русски
		counter = get_counter()

		callback = self.request.get('callback')
		jsonresp = {
			"responseData": {
				"counter": counter,
			}
		}
		incr_counter()

		nejson = json.dumps(jsonresp)
		self.response.out.write(callback + "(" + nejson + ")\r")


application = webapp.WSGIApplication([
	('/trackcounter.*', TrackCounter),
	('/trackjs.*', TrackJS),
	('/track.*', Track),
	],
	debug=True
)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
