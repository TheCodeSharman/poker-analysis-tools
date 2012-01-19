import parser.pokerstars

p1 = parser.pokerstars.PokerStarsHandParser("../tests/PokerStars/showdown.txt")
print p1.parseHand()
