from google.appengine.api import users

import webapp2


class MainPage(webapp2.RequestHandler):

    def get(self):
        user
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
