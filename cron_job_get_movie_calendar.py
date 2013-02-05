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

class Show(db.Model): 
	created = db.DateTimeProperty(auto_now_add=True);
	
	movie=db.StringProperty; #movie name
	time=db.TimeProperty();
	date=db.DateProperty();
	cinema=db.StringProperty; #cinema name
	room=db.StringProperty; #room number
	
	
		
	def __str__(self):
		return self.movie+"|"+str(self.time)+"|"+str(self.date)+"|"+self.cinema+"|"+self.room;
		
	
def new_show(movie="",time=None,date=None,cinema="",room=""):
		show=Show();
		#atributes
		show.movie=movie;
		show.time=time;
		show.date=date;
		show.cinema=cinema;
		show.room=room;
		return show;
		
from csv_download import CSV;
	
from get_cinema_calendar import get_from_24h,get_from_cineplex;

class get_from_mega_star:
	###### private functions ######
	
	#################################		

	def __init__(self):
		print 'Loading from megastar.vn'
		list_show = self.get_mega_star_lich_chieu(self.get_mega_star_info())
		#get final result	
		self.list_show=[];
		for show_info in list_show:
			date=show_info[2];
			m=re.search(r'(\d+)-(\d+)-(\d+)',date);
			if m:
				date=datetime.date(year=int(m.group(3)),day=int(m.group(1)),month=int(m.group(2)) );
			self.list_show+=[ new_show(show_info[0],show_info[1],date,show_info[3],show_info[4])];	
	
	def get_mega_star_lich_chieu(self,html_data):
		list_show_tonghop = []
		listallfilms = html_data.split('<div class="gra_blue_loop float-left"><a target="_blank" href="')
		for lineallfilm in listallfilms:
			namefilms = self.timlink(lineallfilm,'">','</a').strip()
			rapchieuphims = lineallfilm.split('<div class="loop_header"><a target="_blank" href=')
			for linerapchieu in rapchieuphims:
				namerapchieu = self.timlink(linerapchieu,'">','</a').strip()
				listngaychieus = linerapchieu.split('<div class="purple_box"')
				for linengaychieu in listngaychieus:
					namengaychieu = self.timlink(linengaychieu,'>','</').strip()
					listgiochieus = self.munlink(linengaychieu,'&visLang=1")'+";'>",'</a>')	
					for linegiochieu in listgiochieus:
						listchieu = []
						namegiochieu = linegiochieu.strip()
						## ten phim
						listchieu.append(namefilms)
						## gio chieu
						if namegiochieu.find(':') != -1:
							namegiochieus = namegiochieu.split(':')
							try:
								gio = int(namegiochieus[0].strip())
								phut = int(namegiochieus[1].strip())
							except:
								pass
							else:
								namegiochieu  = datetime.time(hour= gio, minute = phut);
						listchieu.append(namegiochieu)
						## ngay chieu
						listchieu.append(namengaychieu)
						## rap chieu
						listchieu.append(namerapchieu)	
						## phong chieu
						listchieu.append('')	
						list_show_tonghop.append(listchieu)
		return list_show_tonghop

	def get_mega_star_info(self):
		value_mega = '1009%2C1006%2C1004%2C1007%2C1001%2C1008%2C1002%2C1005%2C1003'
		#data=urllib2.urlopen('http://www.megastar.vn/msSessionTimeHandles.aspx','RequestType=GetMoviesByCinemas&CinemaIDs='+value_mega+'&visLang=1');
		#html=data.read();
		#data.close();
		
		data = urlfetch.fetch('http://www.megastar.vn/msSessionTimeHandles.aspx','RequestType=GetMoviesByCinemas&CinemaIDs='+value_mega+'&visLang=1', method=urlfetch.POST, deadline=15)
		html = data.content;

		
		listchuaform = ''
		if html.find('value="') != -1:		
			listvaluefilm = self.munlink(html,'value="','"')
			value_mega1 = ''
			for linvaleme in listvaluefilm:
				linvaleme = linvaleme.strip()
				value_mega1 = value_mega1+linvaleme+','
			value_mega1 = value_mega1.replace(listvaluefilm[len(listvaluefilm)-1].strip()+',',listvaluefilm[len(listvaluefilm)-1].strip())
			value_mega1 = urllib.quote_plus(value_mega1.replace('+',' '))
			valuechuan = 'RequestType=GetSessionTime&CinemaIDs='+value_mega+'&Movies='+value_mega1+'&RequestTime=All&visLang=1'
			valuechuan = valuechuan.replace('%2C','%3B')
			valuechuan = valuechuan.replace('&Movies=All%3B','&Movies=')
			#data=urllib2.urlopen('http://www.megastar.vn/msSessionTimeHandles.aspx',valuechuan);
			#html=data.read()
			#data.close();
			
			data = urlfetch.fetch('http://www.megastar.vn/msSessionTimeHandles.aspx',valuechuan, method=urlfetch.POST, deadline=15)
			html = data.content;
			
		return html;	

	def timlink(self,string, start, end):
		str = string.split(start)
		str = str[1].split(end)
		return str[0]
			
	def timnguoc(self,string, start, end):
		str = string.split(start)
		str = str[0].split(end)
		return str[len(str)-1]
	def munlink(self,string, start, end):
		str = string.split(start)
		timlinkdc = []
		bientimlink = 1
		while bientimlink < len(str):
			strtimlink = str[bientimlink].split(end)
			timlinkdc.append(strtimlink[0])
			bientimlink+=1
		return timlinkdc


class get_from_quoc_gia:
	def __init__(self):
		print 'Loading from rap quoc gia'
		###### private functions ######
		def timlink(string, start, end):
			str = string.split(start)
			str = str[1].split(end)
			return str[0]
		def timnguoc(string, start, end):
			str = string.split(start)
			str = str[0].split(end)
			return str[len(str)-1]
		def munlink(string, start, end):
			str = string.split(start)
			timlinkdc = []
			bientimlink = 1
			while bientimlink < len(str):
				strtimlink = str[bientimlink].split(end)
				timlinkdc.append(strtimlink[0])
				bientimlink+=1
			return timlinkdc		
		#################################
		
		list_show = []
#		request = urllib2.Request("http://www.chieuphimquocgia.com.vn/lichphim/Default.aspx?MenuId=14")
#		r = urllib2.urlopen(request)
#		result = r.read()
#		r.close()
#		
		data = urlfetch.fetch("http://www.chieuphimquocgia.com.vn/lichphim/Default.aspx?MenuId=14", method=urlfetch.GET, deadline=15)
		result = data.content;

		
		hangmoves = result.split('<td align="center" valign="top" width="64" style=" padding-top:10px;border-top:solid 1px #FFFFFF; border-left:solid 1px #FFFFFF">')
		linethu = 1 
		while linethu < len(hangmoves):
			
			hangthu2 = hangmoves[linethu].strip()
			daychieu = timlink(hangthu2,'<strong>','<').strip()
			datechieu = timlink(hangthu2,'<br />','<br />').strip()
			if datechieu.find('/') != -1:
				try:
					datechieus = datechieu.split('/')
					ngay = int(datechieus[0].strip())
					thang = int(datechieus[1].strip())
				except:
					pass
				else:
					datechieu = datetime.date(day=ngay,month=thang,year=2012);
			listgiochieu = hangthu2.split('<td align="center" width="50"><font size="1">')
			linegio = 1
			while linegio < len(listgiochieu):
				linegiochieu = listgiochieu[linegio].strip()
				giochieu = timlink(linegiochieu,'<strong>','</').strip()
				hangphongchieu = munlink(linegiochieu,'"><font size="1"><b>','</b>')
				bienphong = 0
				while bienphong < len(hangphongchieu):
					listmoves = []
					linephong = hangphongchieu[bienphong].strip()
					if len(linephong) >= 3:
						linephong = linephong.strip()
						if linephong.find(':') != -1:
							giochieu = linephong.split(':')[0].strip()
							linephong = linephong.split(':')[1].strip()
						else:
							giochieu = giochieu.replace('h','h00')							
						giochieu = giochieu.replace('h',':')
						if giochieu.find(';') != -1:
							listgiochieus = giochieu.split(';')
							biengio = 0
							while biengio < len(listgiochieus):
								listmoves = []
								giochieu1 = listgiochieus[biengio].strip()
								if giochieu1.find(':') != -1:
									try:
										gio = int(giochieu1.split(':')[0].strip())
										phut = int(giochieu1.split(':')[1].strip())
									except:
										pass
									else:
										giochieu1  = datetime.time(hour= gio, minute = phut);
								
								listmoves.append(linephong)
								listmoves.append(giochieu1)
								listmoves.append(datechieu)
								listmoves.append('Rap Quoc Gia')
								if bienphong == 5:
									listmoves.append('phong chieu :4D')
								else:
									listmoves.append('phong chieu :'+str(bienphong+1))
								list_show +=[listmoves]
								biengio+=1
						else:
							giochieu1 = giochieu.strip()
							if giochieu1.find(':') != -1:
								try:
									gio = int(giochieu1.split(':')[0].strip())
									phut = int(giochieu1.split(':')[1].strip())
								except:
									pass
								else:
									giochieu1  = datetime.time(hour= gio, minute = phut);							
							listmoves.append(linephong)
							listmoves.append(giochieu1)
							listmoves.append(datechieu)
							listmoves.append('Rap Quoc Gia')
							if bienphong == 5:
								listmoves.append('phong chieu :4D')
							else:
								listmoves.append('phong chieu :'+str(bienphong+1))
							list_show +=[listmoves]
					bienphong+=1
				linegio+=1
			linethu+=1
		
		#get final result	
		self.list_show=[];
		for show_info in list_show:
			self.list_show+=[ new_show(show_info[0],show_info[1],show_info[2],show_info[3],show_info[4])];
			

class get_movie_calendar(webapp.RequestHandler):
	def get(self):
		csv=CSV();
		csv.type="movie_calendar";
		result="Time:"+str(datetime.datetime.now())+"\n";
		log="";
		failed=0;
		
		for i in range(10):
			try:
				cal=get_from_24h();
				for row in cal.list_show: 
					result+=row.toCSV()+'\n';
			except:
				pass;
			else:
				break;
		else:
			failed+=1;
			log+="Cant get from 24h, there is an error!!!!!!!!!!!!!!!!!!!!!!\n";
		
		for i in range(10):
			try:
				cal=get_from_cineplex();
				for row in cal.list_show: 
					result+=row.toCSV()+'\n';
			except:
				pass;
			else:
				break;
		else:
			failed+=1;
			log+="Cant get from Cineplex, there is an error!!!!!!!!!!!!!!!!!!!!!!\n";
		#print sys.exc_info();
		
		for i in range(10):
			try:
				#24h
				cal=get_from_mega_star();
				for row in cal.list_show: 
					result+=str(row)+'\n';
			except:
				pass;
			else:
				break;
		else:
			failed+=1;
			log+="Cant get from Megastar, there is an error!!!!!!!!!!!!!!!!!!!!!!\n";
		
		if failed<=1:
			csv.content=db.Text(result, encoding="utf-8");
			csv.log=db.Text(log, encoding="utf-8");
			csv.put();
		
		print "Done with Failed=",failed;
		print "Log:\n",log;


def main():
	application = webapp.WSGIApplication([
	('/tasks/get_movie_calendar', get_movie_calendar),
	], debug=True)

	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
