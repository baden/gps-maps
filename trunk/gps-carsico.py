# -*- coding: utf-8 -*-
import logging
from google.appengine.api import images

CarsIcoList

application = webapp.WSGIApplication(
	[
	('/carsico-list.*', CarsIcoList),
	],
	debug=True
)


def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
