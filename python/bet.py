#!/usr/bin/env python 

DEFAULT_ODDS = 10.0/11

def odds_us_to_mult(odds_us):
    if odds_us < 0:
        return -100.0 / odds_us
    elif odds_us > 0: 
        return odds_us / 100.0
        
    elif odds_us == DEFAULT_ODDS:
        return DEFAULT_ODDS
    else:
        return 1.0    

class bet:
    # here's a change
    # odds_us are american odds
    def __init__(self, pick, odds, bet_amount, spread=0, bet_type='NA'):
        self.pick = pick
        self.odds = odds
        self.spread = spread
        self.bet_amount = bet_amount
        self.bet_type = bet_type
        self.outcome = ""

    def calcWinnings(self):
        odds_mult = odds_us_to_mult(self.odds)
        return ((self.bet_amount * odds_mult) + self.bet_amount)
        
    
        
        