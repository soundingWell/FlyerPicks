#!/usr/bin/python

# Mine
from mUser import mUserStats

# Google  
from google.appengine.ext import ndb

# Builtin
import time
import webapp2

# Session Stuff
from gaesessions import get_current_session

def redirect_with_msg(h, msg, dst='/'):
    get_current_session()['msg'] = msg
    h.redirect(dst)
    
def mUserStats_key(userEmail="no_name"):
    """Constructs a Datastore key for a user entity with user email."""
    return ndb.Key('mUserStats', userEmail)

# Shows all existing profiles.
class showAllProfilesPage(webapp2.RequestHandler):
    def get(self):
        # Wait for database to update if a bet was just entered.
        time.sleep(0.2)
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


class profilePage(webapp2.RequestHandler):
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