
class Money(object):
    '''Represents a money amount in a specified currency '''
    AUD, USD, TMONEY = range(3)
    
    def currencyToString(self):
        return [ 'AUD', 'USD', ''][self.currency]
    
    def __init__(self, cents, currency=TMONEY):
        self.cents = cents
        self.currency = currency      # Currency
    
    def __add__(a, b): #@NoSelf
        if a is None and b is None:
            return None
        if a is None:
            return b
        if b is None:
            return a
        if a.currency == b.currency:
            return Money(a.cents + b.cents, a.currency)
        else:
            raise TypeError("Can't add money of different currencies")
        
    def __repr__(self):
        if self.currency == Money.TMONEY:
            return str(self.cents)
        else:
            return "$" + self.currencyToString() + self.cents % 100 + "." + self.cents // 100 
        
        
class Hand(object):
    '''A single hand in a game'''
    HoldEmFixedLimit, HoldEmNoLimit, HoldEmPotLimit = range(3)
    
    def gameTypeToString(self):
        return [
                "HoldEm Fixed Limit",
                "HoldEm No Limit",
                "HoldEm Pot Limit"
               ][self.gameType]
    
    def __init__(self):
        self.numOfSeats = None  # int
        self.gameType = None      # GameType
        self.players = {}         # Player[] hashed by name
        self.rounds = []          # BettingRound[]
        self.ante = None          # Money
        self.totalPot = None     # Money
        self.rake = None          # Money
        self.board = []           # Card[]
        
    def addPlayer(self, player):
        self.players[player.name] = player
    
    def addWinnings(self, winList):
        for w in winList:
            self.players[w[0]].win += w[1]
            
    def addKnownCards(self, cardList):
        for c in cardList:
            self.players[c[0]].startingHand = c[1]
            
    def addBetRound(self, betRound, actionList):
        # add the actions
        betRound.addActions(self, actionList)
        # calculate liveness by removing any players that folded
        if len(self.rounds) > 0:
            betRound.livePlayers = self.rounds[-1].livePlayers.copy()
        for a in betRound.actions:
            if a.action == Action.Fold:
                betRound.livePlayers = betRound.livePlayers.difference([a.player.name])
            elif a.action == Action.Show:
                self.players[a.player.name].startingHand = a.cards
        # append the new bet round
        self.rounds.append(betRound)
    
    def __repr__(self):
        return ("Hand( "
            + "numOfSeats = " + str(self.numOfSeats)
            + ", gameType = \"" + self.gameTypeToString() + "\""
            + ", players = " + str(self.players)
            + ", rounds = " + str(self.rounds)
            + ", ante = " + str(self.ante)
            + ", rake = " + str(self.rake)
            + ", board = " + str(self.board) + " )")

class Player(object):
    '''Represents a player'''
    def __init__(self, name):
        self.name = name
        self.seat = None
        self.win = 0
        self.startingHand = None  # Card[], might be not known
        self.initialStack = None  # Money
    
    def __repr__(self):
        return ("Player( name = \"" + repr(self.name) + "\""
                 + ", seat = " + str(self.seat)
                 + ", win = " + str(self.win)
                 + ", startingHand = " + str(self.startingHand) 
                 + ", initialStack  = " + str(self.initialStack) + "]")

class Card(object):
    '''A card with both value and suit'''
    def __init__(self, value):
        self.value = value[0]      # 2-9, T, J, Q, K, A
        self.suit = value[1]       # d, h, s, c
        
    def __repr__(self):
        return self.value + self.suit
        
        
class BettingRound(object):
    '''What actions each player takes in a betting round'''
    def __init__(self):
        self.pot = None
        self.cards = None
        self.actions = []          # Action[]
        self.rake = None           # Money
        self.livePlayers = None    # set of player id strings
        
    def __repr__(self):
        return ("BettingRound( pot = " + str(self.pot)
                 + ", rake = " + str(self.rake)
                 + ", cards = " + str(self.cards)
                 + ", actions = " + str(self.actions) 
                 + ", livePlayers = " + str(self.livePlayers) + " )")
        
    def addActions(self, hand, actionList):
        # create action objects
        for a in actionList:
            a[1].player = hand.players[ a[0] ]
            self.actions.append(a[1])
        self.livePlayers = set(hand.players.keys())

class Action(object):
    '''The action a player takes'''
    Raise, Bet, ReRaise, Call, Fold, Check, Post, Collect, Show, Muck = range(10)
    
    def actionToString(self):
        return [ "Raise", "Bet", "Reraise", "Call", "Fold", "Check", "Post", "Collect", "Show", "Muck" ][self.action]
    
    def __init__(self):
        self.player = None          # Player
        self.cards = None           # cards shown in a show action
        self.action = None          # ActionType
        self.amount = None             # Money
        self.stack = None           # Money
    
    def __repr__(self):
        return ("Action( player = \"" + repr(self.player.name) + "\""
                  + ", action = " + self.actionToString() 
                  + ", amount = " + str(self.amount)
                  + ", stack = " + str(self.stack) + ")")
        
        
        