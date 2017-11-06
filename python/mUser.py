from bet import bet

from google.appengine.ext import ndb

AGAINST_THE_SPREAD = "ats"
MONEYLINE = "moneyline"

def extract_spread(odds_spread):
    open_p  = odds_spread.find('(')
    if open_p == -1:
        return odds_spread

    spread = odds_spread[0:open_p]

    return spread

def extract_odds(odds_spread):
    open_p  = odds_spread.find('(')
    # Check if it has default odds
    if open_p == -1:
        return '-110'
    close_p = odds_spread.find(')') 
    
    return odds_spread[open_p+1:close_p]


def is_half(odds_spread):
    i = 0 
    while i < 1:
        try: 
            print 'odds: ' + odds_spread
            break;
        except UnicodeEncodeError: 
            print UnicodeEncodeError
            return True
        i += 1
    return False

# Has half refers to the 1/2 symbol.
def convert_oddspread(odds, has_half, if_spread):
    odds_fixed = odds.encode("ascii", "ignore")
 
    # If the original was - 
    if (odds[0] == '-'):   
        if has_half and if_spread:
            as_int = int(odds_fixed[1:len(odds_fixed)]) * -1 
            return (as_int - 0.5)
        else:
            as_float = float(odds_fixed[1:len(odds_fixed)]) * -1 
            return as_float - 0.5
        return as_int
    else: 
        if has_half and if_spread:
            as_int = int(odds_fixed[0:len(odds_fixed)])
            return (as_int + 0.5)
        else:
            as_float = float(odds_fixed[0:len(odds_fixed)])
            return as_float + 0.5


class mUser(ndb.Model):
    user = ndb.UserProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    m_email = ndb.StringProperty(indexed=True)
    m_team_name = ndb.StringProperty(indexed=True)
    m_nickName = ndb.StringProperty(indexed=False)
    

# Inherits from mUser. This is what we actually store.
class mUserStats(mUser, ndb.Model):
    m_betsMade = ndb.IntegerProperty(indexed=False)
    m_betsWon = ndb.IntegerProperty(indexed=False)
    m_balance = ndb.FloatProperty(indexed=False)
    m_currBets = ndb.PickleProperty(indexed=False)
    m_pastBets = ndb.PickleProperty(indexed=False)


    # odds_spread is just odds if moneyline, if ats, then odds/spread must be extracted
    def add_bet(self, pick, odds_spread, event_id, bet_amount, bet_type):
        # Add bet to dictionary 
        print 'event id: ' + event_id
        print 'pick: ' + pick
        print 'bet type: ' + bet_type
        if bet_type == AGAINST_THE_SPREAD:
            has_half = is_half(odds_spread)
            odds = extract_odds(odds_spread)
            spread = extract_spread(odds_spread)
            
            # TODO: figure out a way to do this without_calling this twice.
            odds = convert_oddspread(odds, has_half=False, if_spread=False)
            spread = convert_oddspread(spread, has_half, if_spread=True)
            print 'converted odds: ' + str(odds)
            print 'converted spread: ' + str(spread)
            
            # If you haven't made a bet on this event yet, add this to the
            # dictionary of events. You add a list because you can have multiple
            # bets on an event.
            if event_id not in self.m_currBets:
                self.m_currBets[event_id] = []

            self.m_currBets[event_id].append(bet(pick, odds, float(bet_amount), spread))
        else: 
            odds = convert_oddspread(odds_spread, has_half=False, if_spread=False)
            if  event_id not in self.m_currBets:
                self.m_currBets[event_id] = []
            self.m_currBets[event_id].append(bet(pick, odds, float(bet_amount), 0))
            
        self.m_betsMade += 1
        self.m_balance -= float(bet_amount)
    

    def find_competitor(self, bet, scores_dict):
        for pick in scores_dict:
            if pick != bet.pick:
                return pick 
        return None
    

    def resolve_moneyline(self, bet, scores_dict):
        competitor = self.find_competitor(bet, scores_dict)
        
        # Loss
        if int(scores_dict[bet.pick]) < int(scores_dict[competitor]):
            return "LOSS"
        # Win 
        if int(scores_dict[bet.pick])  > int(scores_dict[competitor]):
            return "WIN"
        # Push
        return "PUSH"
        

    def resolve_ats(self, bet, scores_dict):
        competitor = self.find_competitor(bet, scores_dict)
        
        print 'User Pick: ' + str(scores_dict[bet.pick])
        print 'Opponent: ' + str(scores_dict[competitor])
        # Loss
        if (int(scores_dict[bet.pick]) + bet.spread) < int(scores_dict[competitor]):
            return "LOSS"
        # Win 
        if (int(scores_dict[bet.pick]) + bet.spread) > int(scores_dict[competitor]):
            return "WIN"
        # Push
        return "PUSH"
    

    def resolve_bet(self, scores_dict, event_id, bet, bet_num):
        print "RESOLVE: " + bet.pick + ' ' + str(event_id)
        result = "LOSS"
        if bet.bet_type == "Moneyline":
            result = self.resolve_moneyline(bet, scores_dict)
        else:
            result = self.resolve_ats(bet, scores_dict)
        bet.outcome = result
        
        if result == "PUSH": 
            self.m_balance += bet.bet_amount
        if result == "WIN": 
            print "before_bal: " + str(self.m_balance)
            print "YOU WIN: " + str(bet.calcWinnings())
            self.m_balance += bet.calcWinnings()
            self.m_balance = round(self.m_balance, 2)
            print "bal: " + str(self.m_balance)
            self.m_betsWon += 1
            
        print "RESULT: " + str(result)
        if event_id not in self.m_pastBets:
            self.m_pastBets[event_id] = []
        self.m_pastBets[event_id].append(bet)


        print 'alive: ' + self.m_pastBets[event_id][bet_num].pick
    def resolve_event(self, scores_dict, event_id):
        bet_num = 0 
        for bet in self.m_currBets[event_id]:
            self.resolve_bet(scores_dict, event_id, bet, bet_num)
            bet_num += 1
        del self.m_currBets[event_id]
            