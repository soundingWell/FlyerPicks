# import os
import logging

# appengine_config.py
from google.appengine.ext import vendor

# Add any libraries install in the "third_party" folder.
logging.info('LOSDINGGGGG')
vendor.add('lib')
# vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))


from gaesessions import SessionMiddleware

# suggestion: generate your own random key using os.urandom(64)
# WARNING: Make sure you run os.urandom(64) OFFLINE and copy/paste the output to
# this file.  If you use os.urandom() to *dynamically* generate your key at
# runtime then any existing sessions will become junk every time you start,
# deploy, or update your app!
import os
COOKIE_KEY = 'f6cf247e16bf0848b66ee7f53e0859adb79041e1d957a9e655a692d2b1bbde2eddcbf8ea67cd3cce221a34509e6427f5ecbb245e690b696b186f740d6836d665'

def webapp_add_wsgi_middleware(app):
  #from google.appengine.ext.appstats import recording
  app = SessionMiddleware(app, cookie_key=COOKIE_KEY)
  #app = recording.appstats_wsgi_middleware(app)
  return app

