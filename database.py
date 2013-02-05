from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import datetime
import urllib

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import mail


class Icon(db.Model):
	"""Models an individual Icon """
	created = db.DateTimeProperty(auto_now_add=True);
	whoCreated = db.UserProperty(auto_current_user_add=True);
	whereCreated = db.GeoPtProperty();
	
	modified = db.DateTimeProperty(auto_now=True);
	whoCreated = db.UserProperty(auto_current_user=True);
	whereCreated = db.GeoPtProperty();
	
	thumb = db.StringProperty();
	type = db.StringProperty();
	tag = db.ListProperty(str,default=[]);
	
	numberOfCopy = db.IntegerProperty(default=0);# + 1 for each makeCopy action
	sharingMode = db.StringProperty(choices=set(['public','private']),default='public') ;
	accessUsers = db.ListProperty(users.User,default=[]); # (those have access to icon in private mode) 
	
	content = db.TextProperty();
