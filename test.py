from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import cgi
import datetime
import urllib
import wsgiref.handlers
from operator import itemgetter, attrgetter

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from google.appengine.api import users

from google.appengine.api import mail

import re,urllib,urllib2;

class test(webapp.RequestHandler):
	def get(self):
		pass
		
def main():
	application = webapp.WSGIApplication([
	('/test/test', test),
	], debug=True)

	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
