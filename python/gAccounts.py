#!/usr/bin/python

# Flyer
from mUser import mUserStats

# Google 
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext.webapp import template

# Builtin
import webapp2

# Third party
from gaesessions import get_current_session
from oauth2client import client, crypt 


def mUserStats_key(userEmail="no_name"):
    """Constructs a Datastore key for a user entity with user email."""
    return ndb.Key('mUserStats', userEmail)

   
def redirect_with_msg(h, msg, dst='/'):
    get_current_session()['msg'] = msg
    h.redirect(dst)
    

def is_email_in_our_db(email):
    flyer_accounts = mUserStats.query()
    for account in flyer_accounts:
        print 'email: ' + str(account.m_email)
        if email == account.m_email:
            return account
    return None


def team_name_exists(team_name):
    flyer_accounts = mUserStats.query()
    for account in flyer_accounts:
        if team_name == account.m_team_name:
            return True
    return False


def login_status():
    ls = {}
    ls['gae_status'] = True
    ls['flyer_status'] = True
    
    session = get_current_session()
    gae_user = users.get_current_user()
    
    if gae_user: 
        print 'email: ' + gae_user.email()
        curr_user = is_email_in_our_db(gae_user.email())
        if curr_user:
            if not session:
                session['curr_user'] = curr_user
        else:
            ls['flyer_status'] = False
    if not gae_user: 
        ls['gae_status'] = False
        ls['flyer_status'] = False
    
    return ls


class AuthenticationHandler(webapp2.RequestHandler):
    def post(self):
        
        '''
        gae_user = users.get_current_user()
        if not gae_user:
            return redirect_with_msg(self, 'Login Failed', '/login')

        # get the user's record (ignore TransactionFailedError for the demo)
        # Searches database by email. 
        userDB_key = mUserStats_key(gae_user.email())
        curr_user = mUserStats.get_by_id(gae_user.email(), userDB_key)

        # You have a valid User Account, but not a valid fan_bet account
        if (curr_user == None):
            return redirect_with_msg(self, 'You have a valid Google account, but you do not have a Flyer account', '/createAccount')

        # close any active session the user has since he is trying to login
        session = get_current_session()
        if session.is_active():
            session.terminate()

        # start a session for the user (old one was terminated)
        session['me'] = curr_user
        if session.is_active():
            redirect_with_msg(self, 'success!', '/')
        else:
            print 'session is null when authenticating'
            time.sleep(5)
        '''

        # (Receive token by HTTPS POST)
        
        idtoken = self.request.get('idtoken');
        print 'authenticating: ' + idtoken
         
        try:
            idinfo = client.verify_id_token(idtoken, '716183491616-t8qslj7r9p34kibp1f48r31gjf446pob.apps.googleusercontent.com')
                                        
            # If multiple clients access the backend server:
            if idinfo['aud'] not in ['716183491616-t8qslj7r9p34kibp1f48r31gjf446pob.apps.googleusercontent.com']:
                raise crypt.AppIdentityError("Unrecognized client.")
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise crypt.AppIdentityError("Wrong issuer.")
            #if idinfo['hd'] != APPS_DOMAIN_NAME:
            #    raise crypt.AppIdentityError("Wrong hosted domain.")
        except crypt.AppIdentityError:
            # Invalid token 
            print 'bad token'
        userid = idinfo['sub']
        '''
        path = 'html/authenticated.html'
        self.response.out.write(template.render(path, None))
        '''
 
def checkDuplicateTeamName(team_name):
    print 'hi'
       

class CreateAccount(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(template.render('html/createAccount.html', {}))

    def add_new_user_to_db(self, gae_user, team_name):
        print 'email: ' + str(gae_user.email())
        new_user = mUserStats(m_team_name = team_name, 
                              m_email = gae_user.email(),
                              m_betsMade = 0, 
                              m_betsWon = 0, 
                              m_balance = 2000,
                              m_currBets = {},
                              m_pastBets = {})
        new_user.put() 
        print 'successfully added to db'
        return new_user

    # User has attempted to make a new account.
    # Right now you can only have 1 team per email.
    def post(self):
        session = get_current_session()
        team_name = self.request.get('team_name');
        print 'team name: ' + str(team_name)
        gae_user = users.get_current_user()
        
        # Not logged into google.
        if not gae_user:
            print 'Not logged into Google'
            self.redirect(users.create_login_url())

        # This Google account already exists.
        elif is_email_in_our_db(gae_user.email()):
            print 'User already has account'
            self.redirect('/')

        
        elif team_name_exists(team_name):
            redirect_with_msg(self, "taken", '/createAccount')
        
        # Make new user
        else: 
            new_user = self.add_new_user_to_db(gae_user, team_name)
            session['me'] = new_user
            
        self.redirect('/profile')

        
class deleteProfiles(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        if session.is_active():
            session.terminate()
        
        gprofiles = mUserStats.query()
        
        pcount = 0
        for g in gprofiles:
            g.key.delete()
            pcount += 1
            
        self.response.out.write(str(pcount) + " profiles deleted.")

 
class LogoutHandler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        gae_user = get_current_session()
        
        if session.is_active():
            if session.has_key('me'):
                # update the user's record with total views
                curr_user = session['me']
                curr_user.put()
                session.terminate()
        if gae_user:
            self.response.out.write('GTFO: ' + '[<a href="%s">%s</a>]' 
                                    % (users.create_logout_url('/login'), 'Logout'))
        #else:
        #    redirect_with_msg(self, "Whoops, you weren't logged in", '/resetpassword')

class LogoutAuth(webapp2.RequestHandler):
    def get(self):
        d = {}
        session = get_current_session()
        if session.has_key('msg'):
            d['msg'] = session['msg']
        else:
            d['msg'] = 'you shouldnt be here'
    
        #render_template(self, "resetpassword.html", d) 
