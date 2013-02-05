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

import res


class MainPage(webapp.RequestHandler):
	def get(self):
		user=users.get_current_user()
		if user:
			if user.email()=='tranvietanh1991@gmail.com':greeting = "Welcome Admin! Use ?admin=TVA or /_ah/admin/";
			else:greeting = "Welcome "+user.nickname();
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
		else:
			greeting = "Welcome guest!";
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
		
		template_values = {
			'greeting': greeting,
			'url': url,
			'url_linktext': url_linktext,
		}

		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))

def main():
	application = webapp.WSGIApplication([
	('/[^/]*', MainPage),
	], debug=True)

	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
