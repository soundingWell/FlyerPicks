#!/usr/bin/python

# Builtin
import json 
import webapp2

# Flyer
from sport import sport_parser
from gAccounts import *

# Third Party
from gaesessions import get_current_session

class ncbPage(webapp2.RequestHandler):
    def get(self):
        sp = sport_parser()
        dates_arr = sp.parseXML('NCB')
        open_bets_serialized = json.dumps(dates_arr, sort_keys=True, skipkeys=False, 
                                          indent=2, separators=(',', ': '))

        template_values = {
            'bet_data': open_bets_serialized
        }
        path = 'html/display_ncb.html'
        self.response.out.write(template.render(path, template_values))


class mlbPage(webapp2.RequestHandler):
    def get(self):
        sp = sport_parser()
        dates_arr = sp.parseXML('MLB')
        open_bets_serialized = json.dumps(dates_arr, sort_keys=True, skipkeys=False, 
                                          indent=2, separators=(',', ': '))

        template_values = {
            'bet_data': open_bets_serialized
        }
        path = 'html/display_mlb.html'
        self.response.out.write(template.render(path, template_values))
