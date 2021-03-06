import codecs

class BadAlternative(Exception):
    pass

class Scanner(object):
    def __init__(self):
        self.file_ = None
        self.isEOF = False
        self.acc =""
        self.char_num = 1
        self.line_num = 1
 
    def parseFile(self,fileName):
        self.file_ = codecs.open( fileName, 'r', 'utf_8_sig' )
        
    def parseString(self,s):
        self.acc = s
 
    # Reads a number of characters ahead, only reads them
    # if they haven't already been read
    def readAhead(self, size):
        if size > len(self.acc):
            if self.file_ is None:
                txt = ''
            else:
                txt = self.file_.read( size - len(self.acc) )
            if len(txt) == 0:
                self.isEOF = True
            self.acc += txt

    def peek(self,size):
        self.readAhead(size)
        return self.acc[:size]
    
    # Consumes a number of characters from the read ahead buffer
    def consume(self, size):
        txt = self.acc[0:size]
        self.acc = self.acc[size:]
        
        # The following is purely to keep track of the position
        # with a file for error reporting purposes
        self.char_num += size
        nl = txt.find('\n');
        if nl >= 0:
            self.line_num += txt.count('\n')
            self.char_num = size - nl
        return txt
    
    def consumeWhitespace(self):
        i = 0
        while self.peek(i+1).isspace() and not self.isEOF:
            i = i + 1
        self.consume(i)

    def alternative( self, alts ):
        for alt in alts:
            if self.peek( len(alt) ) == alt:
                self.consume( len(alt) )
                return alt
        raise BadAlternative( 'Expecting one of ' + str(alts) + ' but got \'' + self.peek( len(alt) ) + '\' instead')

    def text( self, text ):
        txt = self.peek( len(text) )
        if txt != text:
            raise BadAlternative( 'Expecting \'' + text + '\' found \'' + txt +'\'') 
        else:
            self.consume( len(text) )
            
    def lookaheadTill(self,text):
        bs = 0
        while self.peek( bs )[-len(text):] != text and not self.isEOF: 
            bs += 1
        return self.peek( bs )[:-len(text)]

