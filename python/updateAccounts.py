import time

# Google Stuff 
##########
#from google.appengine.ext import ndb
from google.appengine.api import background_thread
from google.appengine.ext import ndb
from google.appengine.api import users
#from google.appengine.api import users

# My Stuff
##########
from mUser import mUserStats
from get_results import result_parser

def resolve_bets():
    while True:
        gr = result_parser()
        results_dict = gr.get_results('NBA')
        
        # Get all the users 
        gprofiles = mUserStats.query()
        
        j = 0 
        for event_id in results_dict:
            i = 0 
            for profile in gprofiles:
                
                if j < 1:
                    print i 
                    print profile
                    
                if event_id in profile.m_currBets: # User has a bet on this event
                    profile.resolve_event(results_dict[event_id], event_id)
                    profile.put()
                i += 1
            j += 1
                    
        time.sleep(20)              
        
class updateAccounts():
    
    def __init__(self):
        self.started = True

    def start_thread(self):
        t = background_thread.start_new_background_thread(target=resolve_bets())
    
    
        