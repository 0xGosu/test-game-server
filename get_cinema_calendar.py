import urllib2
import re,sys
import datetime;

class GrabMiss(Exception):
	""" Raise when cant grab infomartion on an expected site 
	@info (Reason miss, Link site)
	"""
	pass;

#multi row with same value in a sql table
class ShowInfo: 
	movie=""; #movie name
	time=""; #datetime.time
	date=""; #datetime.date
	cinema=""; #cinema name
	room=""; #room number
	def __init__(self,movie="",time=None,date=None,cinema="",room=""):
		self.movie=movie;
		self.time=time;
		self.date=date;
		self.cinema=cinema;
		self.room=room;
	
	def toCSV(self):
		return self.movie+"|"+str(self.time)+"|"+str(self.date)+"|"+self.cinema+"|"+self.room;
		
		

class get_from_24h:
	def __init__(self):
		print "Loading from 24h.com.vn";
		self.html_link = self.get_links_box();
		self.links = self.identify_links(self.html_link);
		self.list_show=[];
		for link in self.links:
			try:
				table_data=self.get_main_table_data_of_link(link);
				if not table_data:continue;
				self.list_show+=self.filter_data_in_table(link,table_data);
			except:
				print sys.exc_info();
			else:
				print "Contributed",link,"link!";
		
	def get_links_box(self):
		#left top box contain link to movie calendar of few cinemas	
		data=urllib2.urlopen("http://hn.24h.com.vn/phim-chieu-rap-c285.html");
		html=data.read();
		data.close();
		match=re.search(r'<div class="box_news_box_285_ADS_62_15s_1_headerBoxLeftItem">.+?</div>',html,re.DOTALL);
		if not match:
			print "Not found box contain link at 24h.com.vn";
			raise GrabMiss("Patern for links_box doest match!");
			return None
		html_link=match.group();
		return html_link;
	
	def identify_links(self,html_link):
		#get list of link
		links=re.findall(r'<a href="(.+?)"',html_link);
		print "Found",len(links),"links:",links;
		return links;
	
	def get_main_table_data_of_link(self,link):
		#get main table contain data
		test=urllib2.urlopen(link);
		html_link_test=test.read();
		test.close();
		match=re.search(r'<table class="MsoNormalTable".+?</table>' ,html_link_test,re.DOTALL);
		if match:
			print "----------Found table contain data----------";
			table_data=match.group();
			return table_data;
		else: 
			print "--------Not found table contain data at",link;
			raise GrabMiss("Patern for table_data doest match!",link);
			return None;
		
	def filter_time(self,time_string):
		#filter all time in a string and return a list of datetime.time objects
		times=re.findall(r'(\d+)h(\d+)',time_string);
		filter_dict={}
		for time in times:
			hour=int(time[0]);
			min=int(time[1]);
			filter_dict.setdefault( (hour,min), 1 );
		result=[];
		for time in filter_dict.keys():
			show_time=datetime.time(hour=time[0],minute=time[1]);
			result+=[show_time];
		return result;
	
	def convert_range_date(self,date_string):
		#convert a range date to a list of datetime.date objects
		m=re.search(r'(\d+)/(\d+)-(\d+)/(\d+)',date_string);
		if m:
			start_day=int(m.group(1));
			start_month=int(m.group(2));
			end_day=int(m.group(3));
			end_month=int(m.group(4));
			list_date=[];
			date=datetime.date(day=start_day,month=start_month,year=2012);
			end_date=datetime.date(day=end_day,month=end_month,year=2012);
			while date<=end_date:
				list_date+=[date];
				date=date+datetime.timedelta(days=1);
			return list_date;
	
	def find_cinema_name_in_link(self,link):
		m=re.search(r'rap-quoc-gia',link);
		if m:return "Rap Quoc Gia";
		m=re.search(r'rap-megastar',link);
		if m:return "Rap Megastar";
		return link;
		
	def filter_data_in_table(self,link,table_data):
		list_show=[];
		#find first cinema name to determine this table contain many or 1 cinema 
#		m=re.search(r'<font color="#ffffff" size="2">(.+?)</font>',table_data);
#		if m:
#			cinema_name=self.strip_html_tag_in_string(m.group(1));
#			start=m.start();
#		else:
#			cinema_name=self.find_cinema_name_in_link(link);
#			start=0;
#		#find other cinema 	
#		while 1:
#			cinema_name_pattern=re.compile(r'<font color="#ffffff" size="2">(.+?)</font>');
#			m=cinema_name_pattern.search(table_data,start+1);
#			if m:
#				end=m.start();
#				next_cinema_name=m.group(1);
#			else:
#				end=len(table_data);
#			current_cinema_data=table_data[start:end];
#			print "Cinema name=",cinema_name;
#			show_info=re.findall(r'<font face="Arial">(.+?)</font>',current_cinema_data);
#			if not show_info:
#				raise GrabMiss("Patern for show_info doest match!");
#			
#			for i in range(0,len(show_info),4):
#				if i>=len(show_info):break;
#				movie_shows=[ShowInfo(self.strip_html_tag_in_string(show_info[i]),time,date,cinema_name,"") for time in self.filter_time(show_info[i+1]) for date in self.convert_range_date(show_info[i+2]) ]
#				list_show+=movie_shows;
#			
#			if not m:break;	
#			start=end;
#			cinema_name=next_cinema_name;
			
		##########
		cinemaDataList=re.findall(r'<font color="#ffffff" size="2">(.+?)</font>(.+?)(?=<font color="#ffffff" size="2">|$)',table_data,re.DOTALL);
		
		if not cinemaDataList: #table contain only 1 cinema (fake data for looping)
			cinemaDataList=[( self.find_cinema_name_in_link(link), table_data)];
		
		for cinemaName, cinemaData in cinemaDataList:
			cinemaName=re.sub(r' +',' ', re.sub(r'<.+?>|&.+?;','',re.sub(r'</p>|<br\s*/>','\n',cinemaName),re.DOTALL) ).strip() #html to text  
			print "Cinema name=",cinemaName;
			show_info=re.findall(r'<font face="Arial">(.+?)</font>',cinemaData);
			
			for i in range(0,len(show_info),4):
				if i+2>=len(show_info):break;
				movie_shows=[ShowInfo( re.sub(r' +',' ', re.sub(r'<.+?>|&.+?;','',re.sub(r'</p>|<br\s*/>','\n',show_info[i]),re.DOTALL) ).strip() ,time,date,cinemaName,"") for time in self.filter_time(show_info[i+1]) for date in self.convert_range_date(show_info[i+2]) ]
				list_show+=movie_shows;
			
		if not list_show:
			raise GrabMiss("Patern for show_info or time or date doest match!",link);			
		
		return list_show;
	
#cinema name 
#pattern1_24h="""<font color="#ffffff" size="2">(.+?)</font>""";
#movie >>  room and time >> date >> movie category | in one tr table row
#pattern2_24h="""<font face="Arial">(.+?)</font>""";
	

class get_from_cineplex:
	def __init__(self):
		self.list_show=[];
		print "Loading from platinumcineplex.vn";
		#get html
		data=urllib2.urlopen("http://www.platinumcineplex.vn/vi/lich-chieu.html");
		html=data.read();
		data.close();
		#get list date:
		list_date=self.convert_range_date(html);
			
		#get list row
		list_movie_row=re.findall(r'<div style="width: 100%; height: 35px; float: left">(.+?)(?=<div style="width: 100%; height: 35px; float: left">|<div style="width: 100%; height: 15px; float: left"></div>)',html,re.DOTALL);
		if not list_movie_row:
			print "Unable to grab movie from platinum cineplex!";
			raise GrabMiss("Patern for row doest match!");
			
		#get info in row
		for row in list_movie_row:
			#movie name
			m=re.search(r'<div style="width: 35%; float: left" class="title_yellow">(.+?)</div>',row);
			if m:movie_name=m.group(1);
			else: 
				print "Unable to search for movie name!"
				continue;
			#list_time
			list_time=self.get_list_time(row);
			
			#split row to show()
			movie_shows=[ShowInfo(movie_name,time,date,"Platinum Cineplex","") for time in list_time for date in list_date ]
			self.list_show+=movie_shows;
		
		if not self.list_show:
			raise GrabMiss("Patern for movie_name or list_time doest match!");
		
	
	def convert_range_date(self,html):
		m=re.search(r'<h1 class="componentheading">.+? : (\d+) - (\d+) .+? (\d+)</h1>',html,re.DOTALL);
		#get date
		if m:
			start_day=int(m.group(1));
			start_month=int(m.group(3));
			end_day=int(m.group(2));
			end_month=int(m.group(3));
			list_date=[];
			date=datetime.date(day=start_day,month=start_month,year=2012);
			end_date=datetime.date(day=end_day,month=end_month,year=2012);
			while date<=end_date:
				list_date+=[date];
				date=date+datetime.timedelta(days=1);
			return list_date;
		else:
			raise GrabMiss("Patern for date doest match!");
	
	def get_list_time(self,row):
		list_time=[]
		#get list time (text)
		for text in re.findall(r'<div style="width: 9%; float: left" class="title_yellow_large">(.+?)</div>',row):
			m=re.search(r'(\d+):(\d+)',text);
			if m:
				list_time+=[ datetime.time( hour=int(m.group(1)),minute=int(m.group(2)) ) ];
			else: continue;
		return list_time;


def main():			
#	cal=get_from_24h();
#	for show0 in cal.list_show:print show0.toCSV();
	
	cal2=get_from_cineplex();
	for show2 in cal2.list_show:print show2.toCSV();

	
	

if __name__ == "__main__":
    sys.exit(main())


