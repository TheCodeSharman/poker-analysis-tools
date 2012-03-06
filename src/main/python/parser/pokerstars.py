
import handparser
import scanner

from pokergame import Money, Hand, Player, Card, BettingRound, Action

class PokerStarsHandParser(scanner.Scanner,handparser.HandParser):

    @staticmethod   
    def canParseFile( cls, fileName ):
        parser_ = PokerStarsHandParser( fileName )
        try:
            parser_.readHeader
            return True
        except: # on any exception we assume that this parser can't recognize the file
            return False
        
    def __init__(self, fileName ):
        scanner.Scanner.__init__(self)
        self.parseFile(fileName)
        self.site_name = 'PokerStars'
        self.timezones = ['AEST','ET']
        self.currencies = ['AUD', 'USD']

    def parseHand( self ):
        hand = Hand()
        self.readHeader()
        hand.gameType = Hand.HoldEmNoLimit
        ( hand.numOfSeats, buttonPos ) = self.readTable()
        self.readInitialStacks(hand)
        self.readBlinds(hand)
        self.readHoleCards(hand)
        flop = True
        if ( self.readFlop(hand) ):
            if ( self.readTurn(hand) ):
                if ( self.readRiver(hand) ):
                    self.readShowdown(hand)
        else:
            flop = False
        self.readSummary(hand,flop)
        return hand
    
    def readBlinds(self,hand):
        preflop = BettingRound()
        actions = []
        playerSet = set( hand.players.keys() )
        
        # read small blind 
        pid = self.alternative(playerSet)
        self.text(': posts small blind ')
        act = Action()
        act.action = Action.Post
        act.bet = self.number()
        actions.append( [pid, act] )
        self.text('\n')
        
        # read big blind 
        pid = self.alternative(playerSet)
        self.text(': posts big blind ')
        act = Action()
        act.action = Action.Post
        act.bet = self.number()
        actions.append( [pid, act] )
        self.text('\n')
        
        hand.addBetRound(preflop,actions)
    
    def readHoleCards(self,hand):
        preflop = hand.rounds[0]
        playerSet = set( hand.players.keys() )
        self.text('*** HOLE CARDS ***\n')
        self.text('Dealt to ')
        pid = self.alternative(playerSet)
        self.text(' ')
        hand.players[pid].startingHand = self.readCards()
        self.text('\n')
        actions = self.readBettingActions( preflop, playerSet )
        hand.addBetRound(preflop,actions)
        
    def readFlop(self,hand):
        flopText = '*** FLOP *** '
        if self.peek( len(flopText) ) == flopText:
            self.text( flopText )
            flop = BettingRound()
            flop.cards = self.readCards()
            self.text('\n')
            actions = self.readBettingActions( flop, hand.rounds[-1].livePlayers )
            hand.addBetRound(flop,actions)
            return True
        else:
            return False
        
    def readTurn(self,hand):
        turnText = '*** TURN *** '
        if self.peek( len(turnText) ) == turnText:
            self.text( turnText )
            turn = BettingRound()
            self.readCards()
            self.text(' ')
            turn.cards = self.readCards()
            self.text('\n')
            actions = self.readBettingActions( turn, hand.rounds[-1].livePlayers )
            hand.addBetRound(turn,actions)
            return True
        else:
            return False
        
    def readRiver(self,hand):
        riverText = '*** RIVER *** '
        if self.peek( len(riverText) ) == riverText:
            self.text( riverText )
            river = BettingRound()
            self.readCards()
            self.text(' ')
            river.cards = self.readCards()
            self.text('\n')
            actions = self.readBettingActions( river, hand.rounds[-1].livePlayers )
            hand.addBetRound(river,actions)
            return True
        else:
            return False
        
    def readShowdown(self,hand):
        showdownText = '*** SHOW DOWN ***\n'
        if self.peek( len(showdownText) ) == showdownText:
            self.text( showdownText )
            showdown = BettingRound()
            actions= []
        
            # read showdown actions
            playerSet = hand.rounds[-1].livePlayers.copy()
            while len(playerSet) > 0:
                p = self.alternative(playerSet)
                self.text(': ')
                txt = self.alternative( [ 'shows', 'mucks hand'] )
                if ( txt == 'shows' ):
                    self.text(' ')
                    hand.players[p].startingHand = self.readCards()
                txt = self.lookaheadTill('\n')
                self.consume( len(txt)+1 )
                playerSet = playerSet.difference([p])
            
            # showdown is added as a betting round
            self.readCollectFromPot(actions,hand.rounds[-1].livePlayers)
            hand.addBetRound(showdown,actions)
            return True
        else:
            return False

    def readSummary(self,hand,flop):
        self.text( '*** SUMMARY ***\n' )
        self.text( 'Total pot ')
        self.number()
        self.text( ' | Rake ')
        self.number()
        self.text(' \n')
        if flop:
            self.text('Board ')
            self.readCards()
            self.text('\n')
        for i in range( hand.numOfSeats ):
            self.text('Seat ' + str(i+1) + ': ')
            self.alternative(hand.players.keys())
            txt = self.lookaheadTill('\n')
            self.consume( len(txt)+1 )

    def readBettingActions(self, betRound, livePlayers):
        playerSet = livePlayers.copy()
        actions = []
        more = True
        while more:
            try: 
                p = self.alternative(playerSet)
                self.text(': ')
                actions.append( [p, self.readAction()] )
                self.text('\n')
            except scanner.BadAlternative:
                more = False
        self.readCollectFromPot(actions,playerSet)
                
        return actions
    
    def readCollectFromPot(self,actions,playerSet):                        
        more = True
        alts = playerSet.copy()
        alts.add( 'Uncalled bet (' ) 
        while more:
            try:
                alt = self.alternative( alts )
                amount = None
                if alt == 'Uncalled bet (':
                    amount = self.number()
                    self.text(') returned to ')
                    p = self.alternative(playerSet)
                    actions.append( [p, self.collectMoney(amount) ])
                    self.text('\n')
                else:
                    p = alt
                    if self.alternative( [': doesn\'t show hand \n', ' collected ' ] ) == ' collected ':
                        amount = self.number()
                        actions.append( [p, self.collectMoney(amount) ])
                        self.text(' from pot\n')
            except scanner.BadAlternative:
                more = False
    
    def collectMoney(self,amount):
        act = Action()
        act.action = Action.Collect
        act.amount = amount
        return act
    
    def readAction(self):
        act = Action()
        txt = self.alternative(['folds', 'calls', 'checks', 'bets', 'raises'])
        
        if txt == 'folds' or txt == 'checks':
            self.text(' ')
            if txt == 'folds':
                act.action = Action.Fold
            else:
                act.action = Action.Check
            return act
        
        if txt == 'calls' or txt == 'bets':
            self.text(' ')
            if txt == 'calls':
                act.action = Action.Call
            else:
                act.action = Action.Bet
            act.amount = Money( self.number() )
            return act
        
        if txt == 'raises':
            self.text(' ')
            self.number()
            self.text(' to ')
            act.action = Action.Raise
            act.amount = Money( self.number() ) 
            return act 
        
        raise Exception( 'Unexpected action : "'+txt+'"!!')
        
    def readCards(self):
        cards = []
        self.text('[')
        cards.append(self.readCard())
        while self.peek(1) == ' ':
            self.text(' ')
            cards.append(self.readCard())
        self.text(']')
        return cards

    def readCard(self):
        card = self.alternative('23456789TJQKA')
        card += self.alternative('cshd')
        return Card( card )
    
    def readInitialStacks(self,hand):
        for i in range( hand.numOfSeats ):
            self.text('Seat ' + str(i+1) + ': ')
            
            # Since any character seems to be acceptable in a 
            # player id we scan forward to the end of the line,
            # then look backwards to identify the id.
            # 
            # [we are assuming that \n is invalid in an id]
            
            # look ahead till the in chips text
            txt = self.lookaheadTill('\n')
            e = ' in chips) '
            if txt[-len(e):] != e:
                raise Exception( 'Expecting \'' + e + '\' but found \'' + txt[-len(e):] + '\' instead' )
            
            # parsing backwards we expect to find
            # a number preceded by a '('
            txt = txt[:-len(e)]
            bs = 1
            while txt[-bs:].isdigit():
                bs += 1

            if txt[-bs-1:-bs+1] != ' (':
                raise Exception( 'Expecting (.... in chips)\n')
            
            # so far so good treat the rest of the string
            # as a player id
            player = Player( self.consume( len(txt) - (bs+1) ) )
            
            # parse the rest as normal
            self.text(' (')
            player.initialStack = self.number()
            self.text(' in chips) \n')
            hand.addPlayer( player )
            
    def readTable(self):
        self.text('Table \'')
        self.number()
        self.text(' ')
        self.number()
        self.text('\' ')
        tableSize = self.number()
        self.text('-max Seat #')
        buttonPos = self.number()
        self.text(' is the button\n')
        return ( tableSize, buttonPos )
        
         
    def readHeader( self ):
        self.text('PokerStars Game #')
        self.number()
        self.text(': Tournament #')
        self.number()
        self.text(', ')
        self.money()
        self.text('+')
        self.money()
        self.text(' ')
        self.alternative( self.currencies )
        self.text(' Hold\'em No Limit - Level ')
        self.roman()
        self.text(' (')
        self.number()
        self.text('/')
        self.number()
        self.text(') - ')
        self.date()
        self.text(' ')
        self.time()
        self.text(' ')
        self.alternative( self.timezones )
        self.text(' [')
        self.date()
        self.text(' ')
        self.time()
        self.text(' ')
        self.alternative( self.timezones )
        self.text(']\n')
        
    def date( self ):
        self.number(4)
        self.text('/')
        self.number(2)
        self.text('/')
        self.number(2)
        
    def time( self ):
        self.number(2)
        self.text(':')
        self.number(2)
        self.text(':')
        self.number(2)
        
    def roman( self ):
        bs = 1
        while 'IVXMC'.find( self.peek(bs)[-1] ) != -1:
            bs += 1 
        if bs > 1:
            return self.consume(bs-1)
        else:
            raise Exception( 'Expecting a roman numeral but got \'' + self.peek(1) + '\'')
        
    def money( self ):
        self.text('$')
        self.number(2)
        self.text('.')
        self.number(2)
        
    def number( self, maxsize = -1 ):
        bs = 1
        while self.peek(bs).isdigit() and ( maxsize >= bs or maxsize == -1 ):
            bs += 1
        if bs > 1:
            return int(self.consume(bs-1))
        else:
            raise Exception( 'Expecting a number' )
