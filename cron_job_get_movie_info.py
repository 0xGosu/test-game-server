#!/usr/bin/python
# -*- coding: utf-8 -*-   
# -- coding: iso-8859-15 --

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
from google.appengine.api import urlfetch
from google.appengine.api import mail

import sys;
import re,urllib,urllib2;


from csv_download import CSV;
from get_movie_info import SearchMovie;
import header;			

global log;
log="";
def printf(string):
	global log;
	log+=str(string)+"\n";
			
class get_movie_info(webapp.RequestHandler):
	def get(self):
		csv=CSV();
		csv.type="movie_info";
		result="Time:"+str(datetime.datetime.now())+"\n";
		today=datetime.date.today();
		failed=0;
		global log;
		log='Log'+str(today)+'\n';
		
		##########Get CSV ########
		query = db.Query(CSV, keys_only=False);
		query.filter("type =","movie_calendar");
		query.order("-created");
		data=query.fetch(1);
		mm=re.findall('\n(.+?)\|',data[0].content);
		dict_title={};
		for movie_title in mm:
			movie_title=movie_title.strip();#trim
			movie_title=re.sub(r'\(.+?\)','',movie_title,1);#remove (linh tinh)
			movie_title=re.sub(' +',' ',movie_title);#strip multiple spaces
			dict_title.setdefault(movie_title,''); #save to dict
		#find info and 
		finder=SearchMovie();
		movie_dict={};
		for movie_title in dict_title:
			info=None;
			for i in range(3):#try 3 time;	
				try:
					info=finder.get_movie_info(movie_title);
				except:
					error=str(sys.exc_info());
					pass;
				else:
					break;
			else:
				failed+=1;
				log+=movie_title+' failed: '+str(error)+'\n';
			
			if info==None:continue;
			movie_dict.setdefault(info.title,info);
			
		for title in movie_dict:
			result+=movie_dict[title].toCSV()+'\n';
		
		if failed<=30:
			csv.content=db.Text(result, encoding="utf-8")
			csv.log=db.Text(log)
			csv.put();
			
		print "Done with Failed=",failed;
		print "Log:\n",log;


def main():
	application = webapp.WSGIApplication([
	('/tasks/get_movie_info', get_movie_info),
	], debug=True)

	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
