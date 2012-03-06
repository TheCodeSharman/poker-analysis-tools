'''
Given a game replay each hand for review.
This class contains all the logic related to interpreting the hands 
and actions, it is intended to be decoupled from any GUI code.
'''

class Table(object):
    ''' Represents a table state from a game. '''
    def __init__(self):
        self.numPlayers = 0
        self.holeCards = {}
        self.boardCards = []
        self.stacks = {}

class Replayer(object):
    ''' Keeps track of game state to replay a hand'''
    def __init__(self, game):
        self.game = game
    def nextAction(self): # next action
        pass
    def prevAction(self): # previous action
        pass
    def getTable(self): # returns a Table to represent the current state
        pass