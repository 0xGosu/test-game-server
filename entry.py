from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import cgi
import datetime
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


class Entry(db.Model):
	"""Models an individual text Entry """
	created = db.DateTimeProperty(auto_now_add=True);
	whoCreated = db.UserProperty(auto_current_user_add=True);
	whereCreated = db.GeoPtProperty();
	
	room = db.StringProperty();
	type = db.StringProperty();
	tag = db.ListProperty(str,default=[]);
	content = db.TextProperty();
			

class GetEntry(webapp.RequestHandler):
	def get(self):
		#read header
		currentUser=users.get_current_user();
		
		CityLatLong=self.response.headers['X-AppEngine-CityLatLong'];
		if CityLatLong: 
			CityLatLong=CityLatLong.split(',');
			whereCreated=GeoPt(float(CityLatLong[0]),float(CityLatLong[2]));
			
			self.response.out.write(whereCreated);
		
		#Get var from request
		admin=self.request.get('admin')=="TVA";
				
		room=self.request.get('room');
		
		type=self.request.get_all('type')
		
		tags=self.request.get_all('tag');
		
		maxFetch=self.request.get_range('max',0,1000,default=20);
		offset=self.request.get_range('offset',0,10000,default=0);
		
		keys_only=self.request.get('keys_only');
		
		
		
		#time filter
		dhours=self.request.get('hours');
		dminutes=self.request.get('minutes');
		
		timeString1=self.request.get('timeLowerBound');
		
		
		#Query
		if(keys_only):query = db.Query(Entry, keys_only=True);
		else:query = db.Query(Entry, keys_only=False);
		
		#Filter
		query.filter("room =", room);
		if type:
			query.filter("type IN", type);
		for tag in tags:
			if tag:query.filter("tag =", tag);
		
		if(dhours and dminutes):
			timeFilter=datetime.datetime.now()-datetime.timedelta(hours=int(dhours),minutes=int(dminutes) );
			query.filter("created >",timeFilter);
		if(timeString1):
			time_lower_bound_filter=datetime.datetime.strptime(timeString1,"%Y-%m-%d %H:%M:%S.%f");
			query.filter("created >",time_lower_bound_filter);
		
		#Sort
		query.order("-created");
		
		#Fetch
		data=[];
		if maxFetch>0:
			data = query.fetch(maxFetch,offset);
		else:
			data = [entry for entry in query];
				
		#reversed, most new at bottom
		entries=reversed(data);
		
		#save request var;
		request=Custom();
		request.admin=admin;
		
		#render
			
		template_values = {
			'entries': entries,
			'room' : room,
			'request' : request
		}
		path = os.path.join(os.path.dirname(__file__), 'entry_full.html')
		self.response.out.write(template.render(path, template_values))

	def post(self):
		#Get var from request and pass to data model object
		content=self.request.get('content');
		entry = Entry()
		#entry.userName = self.request.get('userName');
		entry.room = room = self.request.get('room');
		entry.content = content;
		entry.type = self.request.get('type');
		entry.tag = self.request.get_all('tag');
		entry.put() #save data model object to data base
		#render
		template_values = {
			'entries': [entry],
			'room' : room
		}
		path = os.path.join(os.path.dirname(__file__), 'entry_full.html')
		self.response.out.write(template.render(path, template_values))
		

class GetEntryByID(webapp.RequestHandler):
	def get(self):
		IDs=self.request.get_all('id');
		entries=[db.get( db.Key(id) ) for id in IDs];
		
		#render
		template_values = {
			'entries': entries,
			'admin' : False
		}
		path = os.path.join(os.path.dirname(__file__), 'entry_full.html');
		self.response.out.write(template.render(path, template_values));


def main():
	application = webapp.WSGIApplication([
	('/entry/', GetEntry),
	('/entry/byid', GetEntryByID),
	], debug=True)

	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
