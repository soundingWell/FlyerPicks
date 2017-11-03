#!/usr/bin/python

import time

# Web Stuff
##########
import json 
import webapp2

# My Stuff
##########
from sport import sport_parser
from gAccounts import *

# Google Stuff 
##########
from google.appengine.ext.webapp import template

# Session Stuff
##########
from gaesessions import get_current_session
##########

class nbaPage(webapp2.RequestHandler):
    def get(self):
        sp = sport_parser()
        dates_arr = sp.parseXML('NBA')
        serialized = json.dumps(dates_arr, sort_keys=True, skipkeys=False, 
                                indent=2, separators=(',', ': '))
        template_values = {
            'rah': serialized
        }
        path = 'html/display_nba.html'
        self.response.out.write(template.render(path, template_values))

        
        
    def post(self):
        pick_json = self.request.body
        pick_py = json.loads(pick_json)
        print pick_py 
        
        session = get_current_session()
        if (session.has_key('me')):
            #user_key = mUserStats_key(session['me'].m_email)
            #curr_user = mUserStats.get_by_id(session['me'].m_email, user_key)
            curr_user = session['me']
            curr_user.add_bet(pick_py['pick'], pick_py['odds'], pick_py['event_id'], pick_py['bet_amt'], pick_py['bet_type'])
            
            #curr_user.key.delete()
            print "NBA bet successfully added"
            curr_user.put()
            session['me'] = curr_user 
            self.redirect('/profile') 

            # time.sleep(0.1)
            #session['me'] = curr_user
            
        else: 
            print 'session failure'
            self.redirect('/login')