from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import cgi
import datetime,json
import urllib


import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util


from google.appengine.api import users

from google.appengine.api import mail

class Custom():
	pass


from database import Icon
		

class GetIcon(webapp.RequestHandler):
	def get(self):
		#read header
		currentUser=users.get_current_user();
		
		CityLatLong=self.response.headers['X-AppEngine-CityLatLong'];
		if CityLatLong: 
			CityLatLong=CityLatLong.split(',');
			whereCreated=GeoPt(float(CityLatLong[0]),float(CityLatLong[2]));
			
			self.response.out.write(whereCreated);
		
		#Get var from request
		
		matchCurrentUser = self.request.get_all('createdByMe');
		type=self.request.get_all('type')
		tags=self.request.get_all('tag');
		
		maxFetch=self.request.get_range('max',0,100,default=1);
		offset=self.request.get_range('offset',0,10000,default=0);
		
		keys_only=self.request.get('keys_only');
		
		
		
		#time filter
		timeString1=self.request.get('timeLowerBound');
		
		
		#Query
		if(keys_only):query = db.Query(Icon, keys_only=True);
		else:query = db.Query(Icon, keys_only=False);
		
		#Filter
		if matchCurrentUser:
			query.filter("whoCreated =", currentUser);
		if type:
			query.filter("type IN", type);
		for tag in tags:
			if tag:query.filter("tag =", tag);
		
		if(timeString1):
			time_lower_bound_filter=datetime.datetime.strptime(timeString1,"%Y-%m-%d %H:%M:%S.%f");
			query.filter("created >",time_lower_bound_filter);
		
		#Sort
#		query.order("-created");
		
		#Fetch
		data=[];
		if maxFetch>0:
			data = query.fetch(maxFetch,offset);
		else:
			data = [entry for entry in query];
				
		#reversed, most new at bottom
#		entries=reversed(data);
		
		#render
		if(keys_only):
			self.response.out.write(json.dumps( [entry for entry in data]) );
		else:
			self.response.out.write(json.dumps( [entry.dictJSON() for entry in data]) );
		return;

	def post(self):
		#Get var from request and pass to data model object
		entry = Icon()
		entry.content = self.request.get('content');
		entry.thum = self.request.get('thumb');
		entry.type = self.request.get('type');
		entry.tag = self.request.get_all('tag');
		entry.put() #save data model object to data base
		self.response.out.write(entry.dumpsJSON());

class GetIconByID(webapp.RequestHandler):
	def get(self):
		IDs=self.request.get_all('id');
		entries=[db.get( db.Key(id) ) for id in IDs];
		
		self.response.out.write(json.dumps( [entry.dictJSON() for entry in entries]) );
		


def main():
	application = webapp.WSGIApplication([
	('/icon/', GetIcon),
	('/icon/byid', GetIconByID),
	], debug=True)

	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
