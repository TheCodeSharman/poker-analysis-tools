
class Money(object):
    '''Represents a money amount in a specified currency '''
    AUD, USD = range(2)
    def __init__(self, cents, currency):
        self.cents = cents
        self.currency = currency      # Currency
        
        
class Hand(object):
    '''A single hand in a game'''
    HoldEmFixedLimit, HoldEmNoLimit, HoldEmPotLimit  = range(3)
    def __init__(self):
        self.numOfPlayers = None  # int
        self.gameType = None      # GameType
        self.players = {}         # Player[]
        self.rounds = []          # BettingRound[]
        self.winners = []         # Player[]
        self.ante = None          # Money
        self.winAmount = None     # Money
        self.rake = None          # Money
        self.board = []           # Card[]
        
    def addPlayer(self, player):
        self.players[player.name] = player
        
        
class Player(object):
    '''Represents a player'''
    def __init__(self, name):
        self.name = name
        self.startingHand = None  # Card[], might be not known
        self.initialStack = None  # Money


class Card(object):
    '''A card with both value and suit'''
    def __init__(self, value):
        self.value = value[0]      # 2-9, T, J, Q, K, A
        self.suit = value[1]       # d, h, s, c
        
        
class BettingRound(object):
    '''What actions each player takes in a betting round'''
    def __init__(self):
        self.pot = None
        self.actions = []          # Action[]
        self.rale = None           # Money
        
        
class Action(object):
    '''The action a player takes'''
    Raise, Call, Fold, Check, Post = range(5)
    def __init__(self):
        self.player = None          # Player
        self.action = None          # ActionType
        self.bet = None             # Money
        self.stack = None           # Money
        
        
        