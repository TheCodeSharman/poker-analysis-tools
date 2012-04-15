import unittest

from parser.pokerstars import PokerStarsHandParser

class Test(unittest.TestCase):
    def testChecks(self):
        ps = PokerStarsHandParser('../resources/pokerstars/checks.txt')
        ps.parseHand()
        
    def testFlop(self):
        ps = PokerStarsHandParser('../resources/pokerstars/flop.txt')
        ps.parseHand()
        
    def testNoFlop(self):
        ps = PokerStarsHandParser('../resources/pokerstars/no-flop.txt')
        ps.parseHand()
        
    def testReraises(self):
        ps = PokerStarsHandParser('../resources/pokerstars/reraises.txt')
        ps.parseHand()
        
    def testShowdown(self):
        ps = PokerStarsHandParser('../resources/pokerstars/showdown.txt')
        ps.parseHand()
        
    def testMissingSeat(self):
        ps = PokerStarsHandParser('../resources/pokerstars/missingseat.txt')
        ps.parseHand()
        
    def testAllinIn(self):
        ps = PokerStarsHandParser('../resources/pokerstars/allin.txt')
        ps.parseHand()
            
    def testTalk(self):
        ps = PokerStarsHandParser('../resources/pokerstars/talk.txt')
        ps.parseHand() 
                   
    def testOutOfHand(self):
        ps = PokerStarsHandParser('../resources/pokerstars/outofhand.txt')
        ps.parseHand()    
                       
    def testDisconnected(self):
        ps = PokerStarsHandParser('../resources/pokerstars/disconnect.txt')
        ps.parseHand()   
                            
    def testTimedout(self):
        ps = PokerStarsHandParser('../resources/pokerstars/timedout.txt')
        ps.parseHand()
                           
    def testSittingout(self):
        ps = PokerStarsHandParser('../resources/pokerstars/sittingout.txt')
        ps.parseHand()
        
                               
    def testSidepot(self):
        ps = PokerStarsHandParser('../resources/pokerstars/sidepot.txt')
        ps.parseHand()