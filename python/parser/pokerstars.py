import antlr3

import gen.PokerStarsParser
import gen.PokerStarsLexer 
import gen.PokerStarsWalker
 
import parser

class PokerStarsHandParser(parser.HandParser):
    ''' The PokerStars hand parser implementation uses the antlr3 module'''
    @staticmethod
    def createParser( file_name ):
        charStream = antlr3.ANTLRFileStream( file_name, encoding="utf-8")
        lexer = gen.PokerStarsLexer.PokerStarsLexer( charStream )
        tokenStream = antlr3.CommonTokenStream(lexer)
        return gen.PokerStarsParser.PokerStarsParser( tokenStream )

    def __init__(self, file_name):
        self.site_name = 'PokerStars'
        self.parser = self.createParser( file_name )
        
    @classmethod   
    def canParseFile( cls, file_name ):
        parser = cls.createParser( file_name )
        try:
            parser.heading()
            return True
        except: # on any exception we assume that this parser can't recognize the file
            return False
    
    def parseHand(self):
        result = self.parser.game()
        nodeStream = antlr3.tree.CommonTreeNodeStream(result.tree)
        nodeStream.setTokenStream(self.parser.getTokenStream())
        walker = gen.PokerStarsWalker.PokerStarsWalker(nodeStream)
        return walker.game()
       
        