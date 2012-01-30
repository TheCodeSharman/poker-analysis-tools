
class HandParser(object):
    '''Root hand parser class'''
    def __init__(self, file_name):
        self.site_name = None
        self.file_name = file_name
    
    @classmethod    
    def canParseFile( cls, file_name ):
        raise NotImplemented # should return a boolean
    
    def parseHand(self, file_name):
        return NotImplemented # should return a Hand
