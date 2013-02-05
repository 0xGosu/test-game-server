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
	
import mechanize;

import header;

class Show:
	created = db.DateTimeProperty(auto_now_add=True);
	
	name=db.StringProperty; #show name
	time=db.TimeProperty(); #datetime.time
	date=db.DateProperty(); #datetime.date
	channel=db.StringProperty; #channel name
	company=db.StringProperty; #broadcasting company
	
	def new(self,name,time,date,channel,company):
		self.name=name;
		self.time=time;
		self.date=date;
		self.channel=channel;
		self.company=company;
		
	def __str__(self):
		return self.name+"|"+str(self.time)+"|"+str(self.date)+"|"+self.channel+"|"+self.company;

class SCTV:
	def __init__(self):
		"""Init connection to SCTV and collecting tv show
		"""
		self.list_show=[]; #store all show collected
		
		##init browser
		self.browser = mechanize.Browser()
		self.browser.set_handle_robots(False)
		self.cookie = mechanize.LWPCookieJar()
		self.browser.set_cookiejar(self.cookie)
		self.browser.addheaders = [('User-Agent', header.user_agents[6])]
	
	def get_tv_channel(self):
		"""Get all available tv channel of SCTV 
		@return dict (channel id : name)
		"""
		link="http://www.tv24.vn/";
		response = self.browser.open(link)
		html=response.read();
		#find view_state
		m=re.search(r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.+?)"',html,re.DOTALL);
		if m:
			self.view_state=m.group(1);
			#print self.view_state;
		
		m=re.search(r'<select.+?name=".+?\$ddlChannel".+?>.+?</select>',html,re.DOTALL|re.IGNORECASE);
		
		if m:
			channel_and_name=re.findall(r'<option.+?value="(\d+)".*?>(.+?)</option>',m.group());
			self.dict_channel={};
			for element in channel_and_name: 
				self.dict_channel.setdefault(int(element[0]),element[1]);
			return True;
		else:
			return False;
		
	def get_tv_show(self,channel_id,day=None,month=None,year=None): 
		"""Get tv show of SCTV
		@param channel_id id of channel
		@param day specific date, default today
		@param month specific date, default today
		@param year specific date, default today
		"""
		
		today=datetime.date.today();	
		if(not day):day=today.day;
		if(not month):day=today.month;
		if(not year):year=today.year;
		
		link="http://www.tv24.vn/default.aspx";

		params = urllib.urlencode({
			'ScriptManager1':'ctl06$UpdBroadcast|ctl06$btnView',
			'__EVENTTARGET': '',
			'__EVENTARGUMENT': '',
			'__VIEWSTATE': self.view_state,
			'ctl06$ddlChannel': channel_id,
			'ctl06$ddlDay': day,
			'ctl06$ddlMonth': month,
			'ctl06$ddlYear': year,
			'ctl01_ctl01_txtUser_text':'Tên đăng nhập',
			'ctl01$ctl01$txtUser':'',
			'ctl01_ctl01_txtUser_ClientState':'{"enabled":true,"emptyMessage":"Tên đăng nhập"}',
			'ctl01_ctl01_txtPass_text':'',
			'ctl01$ctl01$txtPass':'',
			'ctl01_ctl01_txtPass_ClientState':'',
			'ctl02_cWindowThongBao_ClientState':'',
			'ctl02_RadWindowManager1_ClientState':'',
			'ctl06_txtSearch_text':'Tìm chương trình yêu thích',
			'ctl06$txtSearch':'',
			'ctl06_txtSearch_ClientState':'{"enabled":true,"emptyMessage":"Tìm chương trình yêu thích"}',
			'ctl06$btnView':'',

		});
		response = self.browser.open(link, params)
		html=response.read();
		 
		m=re.search(r' <table cellpadding="0" cellspacing="0" class="calendarl scrollbar">.+?</table>',html,re.DOTALL);		
		if m:
			time_and_name=re.findall(r'<tr><td.+?>(\d+):(\d+)</td><td.+?>(.+?)</td></tr>',m.group());
			date=datetime.date(day=day,month=month,year=year);
			for element in time_and_name:	
				time=datetime.time(hour=int(element[0]), minute=int(element[1]) );
				show=Show();
				show.new(name=element[2],time=time,date=date,channel=self.dict_channel[channel_id],company='SCTV');
				self.list_show+=[show];
				
			return True;
		else: 
			raise Exception("Table Pattern Error");
			return False;


class VCTV:
	def __init__(self):
		"""Init connection to VCTV and collecting tv show
			"""
		self.list_show=[]; #store all show collected
		
		##init browser
		self.browser = mechanize.Browser()
		self.browser.set_handle_robots(False)
		self.cookie = mechanize.LWPCookieJar()
		self.browser.set_cookiejar(self.cookie)
		self.browser.addheaders = [('User-Agent', header.user_agents[6])]
	
	def get_tv_channel(self):
		"""Get all available tv channel of SCTV 
			@return dict (channel id : name)
			"""
		link="http://vctv.vn/lich-phat-song.htm";
		response = self.browser.open(link)
		html=response.read();
		
		m=re.search(r'<select id="lps_channels">.+?</select>',html,re.DOTALL);		
		if m:
			channel_and_name=re.findall(r'<option.+?value="(\d+)".*?>(.+?)</option>',m.group());
			self.dict_channel={};
			for element in channel_and_name: 
				self.dict_channel.setdefault(int(element[0]),element[1]);
			return True;
		else:
			return False;
	
	def get_tv_show(self,channel_id,day=None,month=None,year=None): 
		"""Get tv show of SCTV
			@param channel_id id of channel
			@param day specific date, default today
			@param month specific date, default today
			@param year specific date, default today
			"""
		
		today=datetime.date.today();	
		if(not day):day=today.day;
		if(not month):day=today.month;
		if(not year):year=today.year;
		date=datetime.date(day=day,month=month,year=year);
		link="http://vctv.vn/LichPhatSong.ashx"
		params = urllib.urlencode({
								  'channel':channel_id,
								  'date': str(date),
								  'isAllData':'true',
								  });
		response = self.browser.open(link+'?'+params);
		html=response.read();
						
		time_and_name=re.findall(r'<tr><td class="col1">(\d+):(\d+)</td><td class="col2">(.*?)</td><td class="col3">(.*?)</td></tr>',html);		
		if len(time_and_name):
			for element in time_and_name:	
				time=datetime.time(hour=int(element[0]), minute=int(element[1]) );
				show=Show();
				show.new(name=element[2],time=time,date=date,channel=self.dict_channel[channel_id],company='VCTV');
				if len(show.name.strip())>0:self.list_show+=[show];
			return True;
		else: return False;			

global log;
log="";
def printf(string):
	global log;
	log+=str(string)+"\n";
			
class get_tv_calendar(webapp.RequestHandler):
	def get(self):
		csv=CSV();
		csv.type="tv_calendar";
		result="Time:"+str(datetime.datetime.now())+"\n";
		today=datetime.date.today();
		failed=0;
		global log;
		log='Log'+str(today)+'\n';
		
		##########VCTV########
		cal=VCTV();
		
		for i in range(5): #try 5 time
			try:
				result_get=cal.get_tv_channel();
			except:
				printf(sys.exc_info());
			else:
				break;
		else:
			printf("Cant get list channel from VCTV, Connection error!");
			result_get=None;
		
		if result_get:
			printf("Get list channel VCTV success!");
			for id in cal.dict_channel.keys():
				for i in range(8): # get today and next 7 day
					date=today+datetime.timedelta(days=i);
					for attemp in range(3): #attemt 3 time if not success
						try:
							cal.get_tv_show(id,date.day,date.month,date.year);
						except:
							pass;
						else:
							break;
					else:
						failed+=1;
						printf(str(cal.dict_channel[id])+str(date)+" failed "+str(failed));
						
			#save to result
			for row in cal.list_show: 
				result+=str(row)+'\n';
		
		##########SCTV########
		cal=SCTV();
		
		for i in range(5): #try 5 time
			try:
				result_get=cal.get_tv_channel();
			except:
				printf(sys.exc_info());
			else:
				break;
		else:
			printf("Cant get list channel from SCTV, Connection error!");
			result_get=None;
		
		if result_get:
			printf("Get list channel SCTV success!");
			for id in cal.dict_channel.keys():
				for i in range(8): # get today and next 7 day
					date=today+datetime.timedelta(days=i);
					for attemp in range(3): #attemt 3 time if not success
						try:
							cal.get_tv_show(id,date.day,date.month,date.year);
						except:
							pass;
						else:
							break;
					else:
						failed+=1;
						printf(str(cal.dict_channel[id])+str(date)+" failed "+str(failed));
						
			#save to result
			for row in cal.list_show: 
				result+=str(row)+'\n';
		
		if failed<=6:
			csv.content=db.Text(result, encoding="utf-8")
			csv.log=db.Text(log, encoding="utf-8")
			csv.put();
		
		print "Done with Failed=",failed;
		print "Log:\n",log;


def main():
	application = webapp.WSGIApplication([
	('/tasks/get_tv_calendar', get_tv_calendar),
	], debug=True)

	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
