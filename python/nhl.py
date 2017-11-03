#!/usr/bin/python

import logging
import os 

# Web Stuff
##########
import jinja2
import json 
import webapp2

# My Stuff
##########
from sport import sport_parser

# Google Stuff 
##########
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext.webapp import template

# Session Stuff
##########
from gaesessions import get_current_session
##########

JINJA_ENVIRONMENT = jinja2.Environment(
                                       loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.i18n'],
                                       autoescape=True)

class nhlPage(webapp2.RequestHandler):
    def get(self):        
        logging.info('getting')
        sp = sport_parser()
        dates_arr = sp.parseXML('NHL')

        serialized = json.dumps(dates_arr, sort_keys=True, skipkeys=False, 
                                indent=2, separators=(',', ': '))
        
        template_values = {
            'rah': serialized
        }
        path = 'html/display_nhl.html'
        self.response.out.write(template.render(path, template_values))

           
    def post(self):
        pick_json = self.request.body
        pick_py = json.loads(pick_json)
        print 'bet: ' + str(pick_py)
        
        pick = pick_py['pick']
        spread = pick_py['odds']
        bet_amount = pick_py['bet_amount'] 
        
        print pick
        
        session = get_current_session()
        
        if (session.has_key('me')):
            curr_user = session['me']
            curr_user.add_bet(pick, spread, bet_amount)
            session['me'] = curr_user
            
        else: 
            self.redirect('/login')