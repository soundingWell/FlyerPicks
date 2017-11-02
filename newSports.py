#!/usr/bin/python

import os 
import time


# Web Stuff
##########
import jinja2
import json 
import webapp2

# My Stuff
##########
from sport import sport_parser
from gAccounts import *

# Google Stuff 
##########
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext.webapp import template

# Session Stuff
##########
from gaesessions import get_current_session
##########

class ncbPage(webapp2.RequestHandler):
    def get(self):
        sp = sport_parser()
        dates_arr = sp.parseXML('NCB')

        serialized = json.dumps(dates_arr, sort_keys=True, skipkeys=False, 
                                indent=2, separators=(',', ': '))

        print serialized

        template = JINJA_ENVIRONMENT.get_template('html/display_ncb.html')
        self.response.write(template.render(rah=serialized))  

class mlbPage(webapp2.RequestHandler):
    def get(self):
        sp = sport_parser()
        dates_arr = sp.parseXML('MLB')

        serialized = json.dumps(dates_arr, sort_keys=True, skipkeys=False, 
                                indent=2, separators=(',', ': '))

        print serialized

        template = JINJA_ENVIRONMENT.get_template('html/display_mlb.html')
        self.response.write(template.render(rah=serialized))  

class nflPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('html/import_nfl.html')
        self.response.write(template.render())
        
    def post(self):     # Will receive ajax of bet placed
        pick_json = self.request.body
        pick_py = json.loads(pick_json)
        
        pick = pick_py['pick']
        spread = pick_py['spread']
        bet_amount = pick_py['bet_amount'] 
        
        print pick
        print spread 
        print bet_amount 
        
        session = get_current_session()
        
        if (session.has_key('me')):
            curr_user = session['me']
            curr_user.add_bet(pick, spread, bet_amount)

            session['me'] = curr_user
            
        else: 
            self.redirect('/login')