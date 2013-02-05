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

###Data Model
class User(db.Model):
	"""Models an individual text Entry """
	created = db.DateTimeProperty();
	modified = db.DateTimeProperty(); 
	name = db.StringProperty();
	password = db.StringProperty();
	point = db.IntegerProperty();
	
def showError(self,code,description):
	template_values = {
		'code' : code,
		'detail': description
	}
	path = os.path.join(os.path.dirname(__file__), 'error.html');
	self.response.out.write(template.render(path, template_values));

#Handle Request
class GetUserDetail(webapp.RequestHandler):
	def get(self):
		#Get var from request
		IDs=self.request.get_all('id');
		#Get list of user
		users=[db.get( db.Key(id) ) for id in IDs];
		#render using template
		template_values = {
			'users': users,
			'admin' : (self.request.get('admin') == "TVA")
		}
		path = os.path.join(os.path.dirname(__file__), 'user_full.html');
		self.response.out.write(template.render(path, template_values));

class CreateUser(webapp.RequestHandler):
	def post(self):
		#Name checking
		name=self.request.get('name','');
		#There should be check syntax for username here 
		
		#Key Query to check user name
		query = db.GqlQuery("SELECT __key__ FROM User Where name=:1",name);
		data = query.fetch(1);
		if len(data)>0:
			#show error
			showError(self,1,"Username "+name+" has already in database!");
			return;
		#create user
		user = User();
		user.created = user.modified = datetime.datetime.now();
		user.name = name;
		user.password = self.request.get('password');
		user.point = 0;
		user.put(); #save data model object to data base
		
		#render using template
		template_values = {
			'users': users,
		}
		path = os.path.join(os.path.dirname(__file__), 'user_full.html');
		self.response.out.write(template.render(path, template_values));
		
class GetID(webapp.RequestHandler):
	def get(self):
		#Get var from request
		name=self.request.get('name')
		password=self.request.get('password')
		
		#Key Query to check user name
		query = db.GqlQuery("SELECT __key__ FROM User Where name=:1",name);
		data = query.fetch(3);
		if len(data)<=0:
			#show error code 0
			showError(self,0,"Username "+name+" not found in user database!");
			return;
		
		#check password in list of user have same name (rare)
		for userID in data:
			user=db.get( userID );
			if user.password == password:
				#password is correct , redirect to GetUserDetail
				#render
				template_values = {
					'IDs': [str(user.key())]
				}
				path = os.path.join(os.path.dirname(__file__), 'show_id.html');
				self.response.out.write(template.render(path, template_values));
				return;
		
		#if checking password not successful show error code 2
		showError(self,2,"Password of user "+ name +" is not correct!");
		return;
			
		

class ModifyUserDetail(webapp.RequestHandler):
	def post(self):
		#Get var from request
		id=self.request.get('id');
		password = self.request.get('password');
		point = self.request.get('point');
		
		#get user with id
		user=db.get( db.Key(id) );
		if(user and user.name):
			if(password):user.password = password;
			if(point):
				if point[0]=='+':user.point += int(point[1:]);
				elif point[0]=='-':user.point -= int(point[1:]);
				elif point[0]=='*':user.point *= int(point[1:]);
				elif point[0]=='/':user.point /= int(point[1:]);
				else: user.point = int(point);
			#mark modified	
			user.modified = datetime.datetime.now();
			user.put();
			
			#render using template
			template_values = {
				'users': users,
			}
			path = os.path.join(os.path.dirname(__file__), 'user_full.html');
			self.response.out.write(template.render(path, template_values));
		else:
			#wrong user id show error
			showError(self,3,"User ID is not a correct ID!");


def main():
	application = webapp.WSGIApplication([
	('/user/', GetUserDetail),
	('/user/create', CreateUser),
	('/user/getid', GetID),
	('/user/modify', ModifyUserDetail),
	], debug=True)

	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
