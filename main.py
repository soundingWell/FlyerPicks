#!/usr/bin/python

### Basics ###
import os
import sys
import time
sys.path.append('python/')

# My Stuff
##########
#from sport import sport_parser
from updateAccounts import updateAccounts
from nhl import nhlPage
from nba import nbaPage
from newSports import nflPage
from newSports import ncbPage
from newSports import mlbPage
##########

# Google Stuff 
##########
import appengine_config
from google.appengine.ext import ndb
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import users
##########

# Session Stuff
##########
from gaesessions import get_current_session
##########

# Web Stuff
########## 
import webapp2
import json 
##########

from gAccounts import *
from __builtin__ import False

# [END imports]

providers = {
    'Google'   : 'https://www.google.com/accounts/o8/id'
}

DEFAULT_NICKNAME= "no_name"

def mUserStats_key(userEmail=DEFAULT_NICKNAME):
    """Constructs a Datastore key for a user entity with user email."""
    return ndb.Key('mUserStats', userEmail)
    
def render_template(h, aFile, template_vals):
    path = os.path.join(os.path.dirname(__file__), 'html', aFile)
    h.response.out.write(template.render(path, template_vals))

def redirect_with_msg(h, msg, dst='/'):
    get_current_session()['msg'] = msg
    h.redirect(dst)
    

class AboutHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        current_user = session['me']
        print 'curr: '
        print current_user.m_balance
        
        template_values = {}
        path = 'html/login.html'
        self.response.out.write(template.render(path, template_values))


class MainPage(webapp2.RequestHandler):
    def handle_account(self, gae_status, flyer_status):
        session = get_current_session()
        
        # No Google account
        if not gae_status:
            print 'Forcing google login'
            self.redirect(users.create_login_url(self.request.uri))

        # Have Google Account, but first time at Flyer
        elif gae_status and not flyer_status:
            print 'asking them to make an account.'
            print str(gae_status)
            self.redirect('/createAccount')

        # Good to go. 
        else:
            gae_user = users.get_current_user()
            print gae_user.email()
            curr_user = is_email_in_our_db(gae_user.email())
            if curr_user:
                print 'session started'
                session['me'] = curr_user
            if not curr_user:
                print 'couldnt find user' 
                
        
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
        
class ShowAllProfiles(webapp2.RequestHandler):
    def get(self):
        # Wait for database to update if a bet was just entered.
        time.sleep(0.2)
        session = get_current_session()
        gprofiles = mUserStats.query()
        profile_counter = 0 
        for profile in gprofiles:
            self.response.write('<b>' 'count: </b>' + str(profile_counter) + '<br />')
            self.response.write('<b>' 'name: </b>' + str(profile.m_team_name) + '<br />')
            self.response.write('<b> Email: </b>' + str(profile.m_email) + '<br />')
            if profile.m_currBets:
                print 'bets: ' + str(len(profile.m_currBets))
                for event in profile.m_currBets:
                    for bet in profile.m_currBets[event]:
                        self.response.write(bet.pick + 
                            '<b> spread: </b> ' + str(bet.spread) + 
                            '<b> odds: </b> ' + str(bet.odds) + 
                            '<b> amount: $</b>' + str(bet.bet_amount) +  '<br />') 
            profile_counter += 1


class Profile(webapp2.RequestHandler):
    # This lists the current user's profile.
    def get(self):
        # Wait for database to update if a bet was just entered.
        time.sleep(0.2)
        session = get_current_session()
        gprofiles = mUserStats.query()
        for one_user in gprofiles:
            if one_user.m_email == session['me'].m_email:
                session['me'] = one_user
        
        if session.has_key('me'):
            curr_user = session['me']
            self.response.write('<b> Email: </b>' + str(curr_user.m_email) + '<br />')
            self.response.write('<b> Username: </b>' + str(curr_user.m_nickName) + '<br />')
            self.response.write('<b> Bets made: </b>' + str(curr_user.m_betsMade) + '<br />')
            self.response.write('<b> Bets won: </b>' + str(curr_user.m_betsWon) + '<br />')
            self.response.write('<b> Balance: </b>' + '$' + str(curr_user.m_balance) + '<br />')
            self.response.write('<b> bets: </b>' + '<br />')

            for event in curr_user.m_currBets:
                for bet in curr_user.m_currBets[event]:
                    self.response.write(bet.pick + 
                                        '<b> spread: </b> ' + str(bet.spread) + 
                                        '<b> odds: </b> ' + str(bet.odds) + 
                                        '<b> amount: $</b>' + str(bet.bet_amount) +  '<br />') 
            
            self.response.write('<b> Past Bets: </b>' + '<br />')
            
            for old_event in curr_user.m_pastBets:
                for bet in curr_user.m_pastBets[old_event]:
                    self.response.write(bet.pick + 
                                        '<b> spread: </b> ' + str(bet.spread) + 
                                        '<b> odds: </b> ' + str(bet.odds) + 
                                        '<b> amount: $</b>' + str(bet.bet_amount) +
                                        '<b> Outcome: </b>' + str(bet.outcome) +  '<br />')  
            
        else:
            redirect_with_msg(self, 'Not logged in', '/login')

    
    def post(self):
        # Right now this will delete this user's account
        session = get_current_session()
        if (session.has_key('me')):
            curr_user = session['me']
            userDB_key = mUserStats_key(curr_user.m_email)
            mUserStats.get_by_id(curr_user.m_email, userDB_key).delete()
            session.terminate()
        else:
            self.response.write('ERROR')
            

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
                                       ('/about', AboutHandler),
                                       ('/logout', LogoutHandler),
                                       ('/authenticated', AuthenticationHandler),
                                       ('/resetpassword', LogoutAuth),
                                       ('/deleteProfiles', deleteProfiles),
                                       ('/createAccount', CreateAccount),
                                       ('/profile', Profile),
                                       ('/showAllProfiles', ShowAllProfiles),
                                       ('/nfl', nflPage),
                                       ('/nhl', nhlPage),
                                       ('/nba', nbaPage),
                                       ('/mlb', mlbPage),
                                       ('/ncb', ncbPage),
                                       ('/startChecking', startChecking),
                                       ], debug=True)
 
