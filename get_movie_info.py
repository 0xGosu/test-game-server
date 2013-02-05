#!/usr/bin/python
# -*- coding: utf-8 -*-   
# -- coding: iso-8859-15 --
import sys, string, urllib, urllib2, re, datetime 
import header
import mechanize
from random import randint


class MovieInfo:
	dict_info={};
	def __str__(self):
		return '\n'.join([ self.title,self.year,self.genres,self.release,self.rating,self.directors,self.writers,self.stars
		,self.description,self.posterLink,self.tinyPosterLink,self.youtubeTrailer,self.linkIMDB ]);
			
	def toCSV(self):
		return '|'.join([ self.title,self.year,self.genres,self.release,self.rating,self.directors,self.writers,self.stars
		,self.description,self.posterLink,self.tinyPosterLink,self.youtubeTrailer,self.linkIMDB ]);

class GrabMiss(Exception):
	""" Raise when cant grab infomartion on an expected site 
	@info (Reason miss, Link site)
	"""
	pass;
		
class SearchMovie:
	def __init__(self):
		""" Init connection to imdb
		"""
		self.browser = mechanize.Browser()
		self.browser.set_handle_robots(False)
		self.cj = mechanize.LWPCookieJar()
		self.browser.set_cookiejar(self.cj)
		self.browser.addheaders = [('User-Agent', header.user_agents[6])]
				
	def searchIMDB(self,movie_title): ##get Imdb Body Result
		try:
			response = self.browser.open('http://www.imdb.com/find?s=tt&q='+urllib.quote_plus(movie_title) );
		except urllib2.URLError: #connection error
			print "Unable to connect - searchingIMDB";
		except mechanize.BrowserStateError: #link broken (mechanize)
			print "Broken Link - searchingIMDB";
		
		html=response.read()
		m=re.search("""<a href="(.+?)" onclick=".+?src='/rg/find-tiny-photo-1/title_popular/images/.+?';"><img src="(.+?)" width="23" height="32" border="0"></a>""",html,re.IGNORECASE);
		if m:
			self.tinyPosterLink=m.group(2);
			return 'http://www.imdb.com'+m.group(1);
	
	def get_movie_info(self,movie_title):  ##get imdb info
		"""Get info of a movie with title
		@param title movie's title
		@return an object of class MovieInfo
		"""
		link_imdb = self.searchIMDB(movie_title);
		if not link_imdb: return None;
		try:
			response = self.browser.open(link_imdb);	
		except urllib2.URLError: #connection error
			print "Unable to connect - get_movie_info";
		except mechanize.BrowserStateError: #link broken (mechanize)
			print "Broken Link - get_movie_info";
		
		html=response.read();
			
		m=re.search(r'<td rowspan="2" id="img_primary">.+?<img src="(.+?)".+?temprop="image" /></a>'
		r'\n.+?<h1 class="header" itemprop="name">\s*(.+?)'
		r'\n\s*<span class="nobr">\(<a href=".+?">(\d+)</a>\)</span>'
		r'\n.+?<div class="infobar">(.+?)\s*<span class="nobr">'
		r'\n\s*<a.+?>\s*(.+?)</a></span>'
		r'\n.+?<span itemprop="ratingValue">(.+?)</span>.+?<p itemprop="description">(.+?)</p>'
		r'\n.+?<div class="txt-block">\s*<h4 class="inline">\s*Directors?:\s*</h4>(.+?)</div>'
		r'\n.+?<div class="txt-block">\s*<h4 class="inline">\s*Writers?:\s*</h4>(.+?)</div>'
		r'\n.+?<div class="txt-block">\s*<h4 class="inline">\s*Stars?:\s*</h4>(.+?)</div>'
		,html,re.IGNORECASE|re.DOTALL)
#		0:poster link
#		1:title
#		2:year
#		3:genres (html to text and replace | = ,)
#		4:release date and country (replace &nbsp; = - )
#		5:rating
#		6:description (strip)
#		7:directors (html to text)
#		8:writers (html to text)
#		9:stars (html to text)
		
		if not m: 
			print "Unable to grab!",link_imdb;
			raise GrabMiss("Movie info pattern doesnt match!",link_imdb);
			return None;
		
		movie=MovieInfo();
		
		movie.linkIMDB=link_imdb
		movie.tinyPosterLink=self.tinyPosterLink;
		
		movie.posterLink=m.group(1);
		movie.title=re.sub(r' +',' ', re.sub(r'<.+?>|&.+?;','',re.sub(r'\r|\n|\t',' ',m.group(2)),re.DOTALL) ).strip() #html to text single line
		movie.year=m.group(3);
		movie.genres=re.sub(r'-| +|<.+?>|&.+?;',' ', re.sub(r'<.+?>|&.+?;','',re.sub(r'\r|\n|\t',' ',m.group(4)),re.DOTALL) ).strip().replace('|',','); #html to text
		movie.release=m.group(5).replace('&nbsp;',' - ');
		movie.rating=m.group(6);
		movie.description=m.group(7).strip();
		movie.directors=re.sub(r' +',' ', re.sub(r'<.+?>|&.+?;','',re.sub(r'\r|\n|\t',' ',m.group(8)),re.DOTALL) ).strip() #html to text single line
		movie.writers=re.sub(r' +',' ', re.sub(r'<.+?>|&.+?;','',re.sub(r'\r|\n|\t',' ',m.group(9)),re.DOTALL) ).strip() #html to text
		movie.stars=re.sub(r' +',' ', re.sub(r'<.+?>|&.+?;','',re.sub(r'\r|\n|\t',' ',m.group(10)),re.DOTALL) ).strip() #html to text
		
		#find youtube trailer
		while 1:
			try:
				movie.youtubeTrailer = self.searchYoutubeTrailer(movie.title);
			except:
				movie.youtubeTrailer = '';
			else:
				break;
		
		return movie;
	
	def searchYoutubeTrailer(self,search_query,):
		""" Search for movie trailer on youtube
		@param search_query movie title , year
		@return link of video that match the movie trailer
		"""
		extended=' trailer official';
		response = self.browser.open('http://www.youtube.com/results?search_query='+urllib.quote(search_query+extended));
		html=response.read();
		mm=re.findall(r'<div class="result-item yt-uix-tile yt-tile-default \*sr">.+?(?=<div class="result-item yt-uix-tile yt-tile-default \*sr">)',html,re.DOTALL);
		max=0;
		trailer='';
		for text in mm:
			m=re.search(r'<h3 id="video-long-title-.+?"><a href="(.+?)" class="yt-uix-tile-link" dir="ltr" title="(.+?)"' # link video , title
			r'.+?<a href=.+? class="yt-user-name.+?>(.+?)</a>.+?<span class="viewcount">([\d,]+)' # username of uploader, view count
			,text,re.DOTALL);
			if not m:continue;
			link,title,uploader,view = m.group(1),m.group(2),m.group(3),m.group(4);
			
			#skip video doesnt contain "trailer" in title
			if re.search(r'trailer',title,re.IGNORECASE) == None:continue;
			
			#calculate point of video
			point=0;
			
			#if video title contain official, +2
			if re.search(r'official',title,re.IGNORECASE) :point+=2;
			
			#+1 point for each word or number in search query that movie title contain
			words=re.findall(r'\w+|\d+',search_query);
			for word in words:
				if re.search(word,title,re.IGNORECASE): point+=1;
			
			#if uploader name contain trailer,movie or he is in list famous point +2
			pattern='movie|trailer|film|IGNentertainment|disney';
			if re.search(pattern,uploader,re.IGNORECASE) :point+=2;	
			
			#+1 point for each half milions view count
			view_count=int(view.replace(',',''));
			point+=view_count/500000;
			
			#keep the one that has highest point
			if point>max:
				max=point;
				trailer=link;
		
		if trailer:
			return 'http://www.youtube.com'+trailer;
		else:
			return '';
		
		
def main():			
	global test
	print "Test";
	test=SearchMovie();
	print test.searchIMDB('John Carter');
	print test.get_movie_info('The Lorax');
	
	#movie= test.get_movie_info('John Carter');
	
if __name__ == "__main__":
    sys.exit(main())