#!/usr/bin/python

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

    def add_bet(self, curr_user, pick_data):
        curr_user.add_bet(pick=pick_data['pick'],
                          odds_spread=pick_data['odds'],
                          event_id=pick_data['event_id'],
                          bet_amount=pick_data['bet_amt'],
                          bet_type=pick_data['bet_type'])
        
           
    def post(self):                
        session = get_current_session()
        if (session.has_key('me')):
            curr_user = session['me']
            pick_data = json.loads(self.request.body)
            self.add_bet(curr_user, pick_data)
            curr_user.put()
            
            # Update the session.
            session['me'] = curr_user
            
        else: 
            self.redirect('/login')