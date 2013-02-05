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

class MainPage(webapp.RequestHandler):
	def get(self):
		self.error(404);
		
class Login(webapp.RequestHandler):
	def get(self):
		user=users.get_current_user()
		if user:
			self.response.out.write("Login Success")
		else:
			if self.request.get('check'):
				self.response.out.write("Not yet Login")
			else:
				url = users.create_login_url(self.request.uri)
			self.redirect(url);

class Logout(webapp.RequestHandler):
	def get(self):
		user=users.get_current_user()
		if not user:
			self.response.out.write("Logout Success")
		else:
			url = users.create_logout_url(self.request.uri)
			self.redirect(url);
			
def main():
	application = webapp.WSGIApplication([
	('/auth/[^/]*', MainPage),
	('/auth/login/[^/]*', Login),
	('/auth/logout/[^/]*', Logout),
	], debug=True)

	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
