from google.appengine.dist import use_library
use_library('django', '1.2')

import os
import cgi
import datetime
import urllib,urllib2,cookielib,re
import wsgiref.handlers
from operator import itemgetter, attrgetter
from google.appengine.api import images

from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util



from google.appengine.api import users

from google.appengine.api import mail

from google.appengine.api import images

from google.appengine.api import urlfetch

from google.appengine.api import taskqueue

class Image(db.Model):
	"""Models an individual Image """
	created = db.DateTimeProperty(auto_now_add=True);
	tag = db.ListProperty(str,default=[]);
	thumb = db.BlobProperty();
	content = db.BlobProperty();
	

class GetImage(webapp.RequestHandler):
	def get(self):
		
		img_id=self.request.get('img_id');
		name=self.request.get('name');
		thumb=self.request.get('thumb');
		
		image=None;#get image
		if(img_id):image = db.get(img_id);
		if(not image and name):image = db.get(db.Key.from_path('Image',name));
		
		if not image:
			m=re.search(r'.+/(.+)\.(.*?)(?:\.html|$)',self.request.url ) # get filename and extension of a link download
			if m:
				fileName=m.group(1);
				try:
					image=db.get(fileName);
				except:
					pass;
				if not image: image=db.get(db.Key.from_path('Image',fileName));
				
		if image:
			self.response.headers['Content-Type'] = "image/png";
			if thumb:
				self.response.out.write(image.thumb);
			else:
				self.response.out.write(image.content);
		else:
			self.error(404)
			
class CreateImage(webapp.RequestHandler):
	def post(self):
		#Get var from request and pass to data model object
		content=self.request.get('content');
		name=self.request.get('name');
		thumb=self.request.get('thumb');
		error=img_id="";
		if content:
			image=None;
			if name:
				if not db.get(db.Key.from_path('Image',name)):image = Image(key_name=name);
				else:error="Name conflict";
			#bypass image name if conflict
			if not image:image =Image();
			#upload image
			if image:
				image.tag =self.request.get_all('tag');
				if thumb:
					pimage = images.Image(image_data=content);
					#crop to square
					if pimage.width<pimage.height:
						pimage.crop(0.0,0.0,1.0,1.0*pimage.width/pimage.height);
					else:
						pimage.crop(0.0,0.0,1.0*pimage.height/pimage.width,1.0);
					#resize to thumbSize	
					pimage.resize(thumbSize);
					#execute
					thumbImage=pimage.execute_transforms(output_encoding=images.PNG, quality=None );
#					thumbImage = images.resize(content, 120, 120);
				if thumb and thumb!='content':
					image.thumb = db.Blob(thumbImage);
				if thumb=='content':
					image.content = db.Blob(thumbImage);
				else:	
					image.content = db.Blob(str(content));
				
				image.put() #save data model object to data base
				img_id=str(image.key());
					 
				
		else:
			error="No content";
		#render
		template_values = {
			'error': error,
			'img_id' : img_id,
			'host_url' : self.request.host_url,
		}
		path = os.path.join(os.path.dirname(__file__), 'upload_image_success.html')
		self.response.out.write(template.render(path, template_values))
		
class UploadImage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'upload_image.html')
		self.response.out.write(template.render(path, {}))

class RemoteUploadImage(webapp.RequestHandler):
	
	def get(self):
		self.remoteUpload();
	def post(self):
		self.remoteUpload();
	
	def remoteUpload(self):
		#Get var from request and pass to data model object
		url=self.request.get('url');
		name=self.request.get('name');
		thumb=self.request.get('thumb');
		error=img_id="";
		content=None;
		thumbSize=120;
		try:
			data=urlfetch.fetch(url,method=urlfetch.GET, deadline=60);
			content=data.content;
		except:	
			error="Leech error";
			
		if content:
			image=None;
			if name:
				image=db.get(db.Key.from_path('Image',name));
				if not image:image = Image(key_name=name);
				else:
					error="Name conflict override";
					#overide content to current image
			else:
				image=Image();
			#upload image
			if image:
				image.tag =self.request.get_all('tag');
				if thumb:
					pimage = images.Image(image_data=content);
					#crop to square
					if pimage.width<pimage.height:
						pimage.crop(0.0,0.0,1.0,1.0*pimage.width/pimage.height);
					else:
						pimage.crop(0.0,0.0,1.0*pimage.height/pimage.width,1.0);
					#resize to thumbSize	
					pimage.resize(thumbSize);
					#execute
					thumbImage=pimage.execute_transforms(output_encoding=images.PNG, quality=None );
#					thumbImage = images.resize(content, 120, 120);
				if thumb and thumb!='content':
					image.thumb = db.Blob(thumbImage);
				if thumb=='content':
					image.content = db.Blob(thumbImage);
				else:
						
					image.content = db.Blob(str(content));
				
				image.put() #save data model object to data base
				img_id=str(image.key());
					 
				
		else:
			error="No content";
		#render
		template_values = {
			'error': error,
			'img_id' : img_id,
			'img_name' : name,
			'host_url' : self.request.host_url,
		}
		path = os.path.join(os.path.dirname(__file__), 'upload_image_success.html')
		self.response.out.write(template.render(path, template_values))
	
	

class TaskRemoteUploadImage(webapp.RequestHandler):
	def get(self):
		#Get var from request and pass to data model object
		url=self.request.get('url');
		name=self.request.get('name');
		thumb=self.request.get('thumb');
		taskqueue.add(url='/image/remote_upload/', params={'url': url, 'thumb':thumb , 'name': name } ,queue_name='photoLeecher');
		
		error="Waiting for process";
		template_values = {
				'error': error,
				'img_id' : '',
				'img_name' : name,
				'host_url' : self.request.host_url,
			}
		path = os.path.join(os.path.dirname(__file__), 'upload_image_success.html')
		self.response.out.write(template.render(path, template_values))
		

def main():
	application = webapp.WSGIApplication([
	('/image/[^/]*$', GetImage),
	('/image/create/', CreateImage),
	('/image/upload/', UploadImage),
	('/image/remote_upload/', RemoteUploadImage),
	('/image/task_remote_upload/', TaskRemoteUploadImage),
	], debug=True)

	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
