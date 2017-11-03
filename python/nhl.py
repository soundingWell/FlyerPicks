#!/usr/bin/python

import logging

# Web Stuff
##########
import json 
import webapp2

# My Stuff
##########
from sport import sport_parser

# Google Stuff 
##########
from google.appengine.ext.webapp import template

# Session Stuff
##########
from gaesessions import get_current_session
##########

class nhlPage(webapp2.RequestHandler):
    def get(self):        
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
        session = get_current_session()
        
        if (session.has_key('me')):
            curr_user = session['me']
            curr_user.add_bet(pick, spread, bet_amount)
            session['me'] = curr_user
            
        else: 
            self.redirect('/login')