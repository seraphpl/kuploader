import os
import urllib
import webapp2

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers


class UserFile(ndb.Model):
    user = ndb.StringProperty()
    file_name = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()


class MainHandler(webapp2.RequestHandler):
    def get(self):
        files = UserFile.query(
            UserFile.user == users.get_current_user().user_id()
        ).fetch()
        upload_url = blobstore.create_upload_url('/upload')
        self.response.out.write('<html><body>')
        self.response.out.write('%s<br><a href="%s">Logout</a><br>' %
                                (users.get_current_user().nickname(),
                                users.create_logout_url(self.request.uri)))
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit"
            name="submit" value="Submit"> </form>""")
        for file in files:
            self.response.write('<a href="%s">%s</a><br>' % 
                                ('/serve/%s' % file.blob_key, file.file_name))
        self.response.out.write('</body></html>')


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        user_file = UserFile(user=users.get_current_user().user_id(),
                             file_name=blob_info.filename,
                             blob_key=blob_info.key())
        user_file.put()
        self.redirect('/')


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info, save_as=True)


application = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/upload', UploadHandler),
    ('/serve/([^/]+)?', ServeHandler)], debug=True)

