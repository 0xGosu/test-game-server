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

class CSV(db.Model):
	created = db.DateTimeProperty(auto_now_add=True);
	type= db.StringProperty();
	content = db.TextProperty();
	comment = db.StringProperty();
	log = db.TextProperty();
	
class GetCSV(webapp.RequestHandler):
	def get(self):
		type_filter=self.request.get("type");
		time_filter=self.request.get("time");
		
		query = db.Query(CSV, keys_only=False);
		if(type_filter):query.filter("type =",type_filter);
		query.order("-created");
		data=query.fetch(1);
		if data:
			csv=data[0];
			self.response.headers['Content-Type'] = "text/plain; charset=utf-8";
			self.response.out.write(csv.content);
		else:
			self.error(404);
		
		
def main():
	application = webapp.WSGIApplication([
	('/csv/', GetCSV),
	], debug=True)

	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
