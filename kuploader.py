import os
import urllib
import jinja2
import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class FileModel(ndb.Model):
    user = ndb.UserProperty()
    file_name = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()


class MainHandler(webapp2.RequestHandler):
    def get(self):
        files = FileModel.query(
            FileModel.user == users.get_current_user()
        ).fetch()
        upload_url = blobstore.create_upload_url('/upload')
        logout_url = users.create_logout_url('/')
        template_values = {
                'files': files,
                'upload_url': upload_url,
                'logout_url': logout_url,
                'user': users.get_current_user(),
                'admin': users.is_current_user_admin()
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        # 'file' is file upload field in the form
        upload_files = self.get_uploads('file')
        if len(upload_files) <= 0:
            self.redirect('/')
            return
        blob_info = upload_files[0]
        user_file = FileModel(user=users.get_current_user(),
                             file_name=blob_info.filename,
                             blob_key=blob_info.key())
        user_file.put()
        self.redirect('/')


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info, save_as=True)


class RemoveHandler(webapp2.RequestHandler):
    def get(self, file_id):
        file = FileModel.get_by_id(int(file_id))
        if file:
            file.key.delete()
        self.redirect(self.request.referer)


class AdminHandler(webapp2.RequestHandler):
    def get(self):
        files = FileModel.query().order(FileModel.user).fetch()
        logout_url = users.create_logout_url(self.request.uri)
        template_values = {
                'files': files,
                'logout_url': logout_url,
                'user': users.get_current_user(),
                'admin': users.is_current_user_admin()
        }

        template = JINJA_ENVIRONMENT.get_template('admin.html')
        self.response.write(template.render(template_values))
    

application = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/upload', UploadHandler),
    ('/admin', AdminHandler),
    ('/serve/([^/]+)?', ServeHandler),
    ('/remove/([^/]+)?', RemoveHandler),
], debug=True)
