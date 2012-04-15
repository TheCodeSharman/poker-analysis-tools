_parserPlugins = []

def registerParserPlugin( p ):
    _parserPlugins.append( p )
    
def findParserForFile( file_name):
    for p in _parserPlugins:
        if p.canParseFile( file_name):
            return p(file_name)
        
def parseFile( file_name):
    parser = findParserForFile( file_name )
    hands = []
    while parser.moreHands():
        hands.append( parser.parseHand())
    return hands  

class HandParsingException(Exception):
    ''' Describes an exception parsing a poker history file'''
    def __init__(self, hand_id, line_num, char_num, message ):
        self.line_num = line_num
        self.char_num = char_num
        self.hand_id = hand_id
        self.message = message
    def __str__(self):
        return "Error parsing hand at line %d, column %d: %s"%(self.line_num,self.char_num,self.message)

class HandParser(object):
    '''Root hand parser class'''
    def __init__(self, file_name):
        self.site_name = None
        self.file_name = file_name
    
    @staticmethod    
    def canParseFile( file_name ):
        raise Exception('Not implemented') # should return a boolean
    
    def moreHands(self):
        raise Exception('Not implemented') # return an bool
    
    def parseHand(self):
        return Exception('Not implemented') # should return a Hand
