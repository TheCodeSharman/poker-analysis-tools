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