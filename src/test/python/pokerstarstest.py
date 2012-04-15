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
                    
    def testFpp(self):
        ps = PokerStarsHandParser('../resources/pokerstars/fpp.txt')
        ps.parseHand()
        
    def testConnected(self):
        ps = PokerStarsHandParser('../resources/pokerstars/connected.txt')
        ps.parseHand()
                    
    def testFoldShows(self):
        ps = PokerStarsHandParser('../resources/pokerstars/foldshows.txt')
        ps.parseHand()  
                    
    def testWinsmoney(self):
        ps = PokerStarsHandParser('../resources/pokerstars/winsmoney.txt')
        ps.parseHand()

    def testFreeroll(self):
        ps = PokerStarsHandParser('../resources/pokerstars/freeroll.txt')
        ps.parseHand()  
                       
    def testSidepot2(self):
        ps = PokerStarsHandParser('../resources/pokerstars/sidepot2.txt')
        ps.parseHand()
                          
    def testAllinbb(self):
        ps = PokerStarsHandParser('../resources/pokerstars/allinbb.txt')
        ps.parseHand()
                 
    def testAntes(self):
        ps = PokerStarsHandParser('../resources/pokerstars/antes.txt')
        ps.parseHand()
                         
    def testRebuy(self):
        ps = PokerStarsHandParser('../resources/pokerstars/rebuy.txt')
        ps.parseHand()
                         
    def testTimedoutdis(self):
        ps = PokerStarsHandParser('../resources/pokerstars/timedoutdis.txt')
        ps.parseHand()
     
    def testMatch(self):
        ps = PokerStarsHandParser('../resources/pokerstars/match.txt')
        ps.parseHand()
        
    def testWinstourn(self):
        ps = PokerStarsHandParser('../resources/pokerstars/winstourn.txt')
        ps.parseHand()
        
        
    def testKnockout(self):
        ps = PokerStarsHandParser('../resources/pokerstars/knockout.txt')
        ps.parseHand()