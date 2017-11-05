#!/usr/bin/python

# Builtin
import webapp2
import sys
sys.path.append('python/')

# My Stuff
from updateAccounts import updateAccounts
from nhl import nhlPage
from nba import nbaPage
from newSports import nflPage
from newSports import ncbPage
from newSports import mlbPage
from flyer_profile import profilePage
from flyer_profile import showAllProfilesPage
from gAccounts import *
from mUser import mUserStats

# Google
from google.appengine.ext.webapp import template
from google.appengine.api import users

# Session
from gaesessions import get_current_session


class MainPage(webapp2.RequestHandler):
    def handle_account(self, gae_status, flyer_status):
        # No Google account, force Google login.
        if not gae_status:
            self.redirect(users.create_login_url(self.request.uri))

        # Have Google Account, but first time at Flyer
        elif gae_status and not flyer_status:
            print str(gae_status)
            self.redirect('/createAccount')

        # They are logged into Google and have a Flyer account.
        else:
            print 'Logged in'
        
                
        
    def get(self):
        ls = login_status()
        self.handle_account(ls['gae_status'], ls['flyer_status'])
        template_values = {
                'flyer_status': False,
                'gae_status': False
        }
        path = 'html/basicHomePage.html'
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        # The user hit logout. They need to login. 
        self.redirect(users.create_logout_url("/"))


# This is supposed to to start a thread that will check on the status 
# of games at a regular interval and update accounts as games finish.
# I'm scared to run it as of now because it's not working right.
class startChecking(webapp2.RequestHandler):
    def get(self):
        print 'dont do anything'
        #ua = updateAccounts()
        #ua.start_thread() 

app = webapp2.WSGIApplication([
                                       ('/', MainPage),
                                       ('/logout', LogoutHandler),
                                       ('/authenticated', AuthenticationHandler),
                                       ('/resetpassword', LogoutAuth),
                                       ('/deleteProfiles', deleteProfiles),
                                       ('/createAccount', CreateAccount),
                                       ('/profile', profilePage),
                                       ('/showAllProfiles', showAllProfilesPage),
                                       ('/nfl', nflPage),
                                       ('/nhl', nhlPage),
                                       ('/nba', nbaPage),
                                       ('/mlb', mlbPage),
                                       ('/ncb', ncbPage),
                                       ('/startChecking', startChecking),
                                       ], debug=True)
 
