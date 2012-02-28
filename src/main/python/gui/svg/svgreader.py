'''
This is a somewhat incomplete and minimalistic SVG parser
that can render to a pycairo context which should be adequate
for most needs.

It purpose is to create a way of rendering vector graphics easily
in Python rather than being a general purposes SVG renderer.

i.e. the SVG files are tailored to work with this parser.

TODO: No reason why this can't be made a compliant SVG
implementation, just needs the effort :-)

Implementation is via xml.etree.ElementTree and the
pyparsing declarative EBNF based string parser.
 
see also http://www.w3.org/TR/SVG/
'''
import xml.etree.ElementTree as ET
import math

from pyparsing import Word, ParserElement, Optional, nums, Combine, CaselessLiteral, oneOf, ZeroOrMore, srange, Dict, Suppress, Group, OneOrMore #@UnresolvedImport
ParserElement.enablePackrat()

'''Load an SVG file returns an SvgNode '''
def loadSvgFile(fileName):
    return Svg( ET.parse(fileName).getroot() )

'''Implement this interface to the render a SVG, see SvgCairoRenderer for example'''
class SvgRenderer(object):
    
    def enterGroup(self,matrix):
        pass
    
    def exitGroup(self):
        pass
    
    def setStyle(self, style):
        pass
    
    def rectangle(self, x, y, width, height):
        pass
    
    def roundedRectangle(self, x, y, width, height, rx, ry ):
        pass
    
    def curve(self,rel,x1,y1,x2,y2,x3,y3):
        pass
    
    def line(self,rel,x,y):
        pass
    
    def move(self,rel,x,y):
        pass
    
    def closePath(self):
        pass
    
    def getCurrentPoint(self):
        pass
    
    def render(self):
        pass

# What follows is a mixture of etree, pyparsing and some basic string function based parsing.
# I've avoided using regular expressions because I find the code, whislt terse is very
# difficult to maintain. Pyparsing seems to do a good job of keeping code clean.
commaWsp = Optional(',').suppress()
digitSequence = Word( nums )
sign = oneOf( '+ -' )
integerConstant = digitSequence
fractionalConstant = digitSequence + Optional( '.' +  digitSequence ) | '.' +  digitSequence 
exponent = oneOf( 'e E' ) + Optional( sign ) + digitSequence

number = Combine( Optional( sign ) + fractionalConstant + Optional( exponent ) )
number.setParseAction( lambda t: float( t[0]))

angle = number + ( CaselessLiteral('deg') | CaselessLiteral('grad') | CaselessLiteral('rad') )

''' Represents a matrix '''
class SvgMatrix(object):
    def __init__(self, a, b, c, d, e, f ):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
    def __eq__(a,b): #@NoSelf
        return a.a == b.a and a.b == b.b and a.c == b.c and a.d == b.d and a.e == b.e and a.f == b.f
    def __repr__(self):
        return 'matrix(' + str(self.a) +',' + str(self.b) + ',' + str(self.c) + ',' + str(self.d) + ',' + str(self.e) + ',' + str(self.f) +')'

class SvgTranslate(SvgMatrix):
    def __init__(self, tx, ty):
        SvgMatrix.__init__(self, 1, 0, 0, 1, tx, ty)
    def __repr__(self):
        return 'translate(' + str(self.e) + ',' + str(self.f) + ')'
    
class SvgScale(SvgMatrix):
    def __init__(self, sx, sy):
        SvgMatrix.__init__(self, sx, 0, 0, sy, 0, 0)
    def __repr__(self):
        return 'scale(' + str(self.a) + ',' + str(self.d) + ')'
    
class SvgRotate(SvgMatrix):
    def __init__(self, angle, cx, cy):
        cs = math.cos(angle)
        sn = math.sin(angle)
        SvgMatrix.__init__(self, cs, sn, -sn, cs, cx - cs*cx + sn*cy, cy - sn*cx - cs*cy )

class SvgSkewX(SvgMatrix):
    def __init__(self, angle ):
        tn = math.tan(angle)
        SvgMatrix.__init__(self, 1, 0, tn, 1, 0, 0)
    
class SvgSkewY(SvgMatrix):
    def __init__(self, angle ):
        tn = math.tan(angle)
        SvgMatrix.__init__(self, 1, tn, 0, 1, 0, 0)

matrix = 'matrix' + '(' + number('a') + commaWsp \
                + number('b') + commaWsp \
                + number('c') + commaWsp \
                + number('d') + commaWsp \
                + number('e') + commaWsp \
                + number('f') + ')'
matrix.setParseAction( lambda t : SvgMatrix( t.a, t.b, t.c, t.d, t.e, t.f ) )

translate = 'translate' + '(' + number('tx') + commaWsp + Optional( number('ty') ) + ')'
translate.setParseAction( lambda t : SvgTranslate( t.tx, t.ty ) )

scale = 'scale' + '(' + number('sx')  + commaWsp + Optional( number('sy') )  + ')'
scale.setParseAction( lambda t : SvgScale( t.sx, t.sy ) )

rotate = 'rotate' + '(' + number('angle') + Optional( commaWsp + number('cx') + commaWsp + number('cy')  ) + ')'
rotate.setParseAction( lambda t : SvgRotate( t.angle, t.cx, t.cy ) )

skewX = 'skewX' + '(' + number('angle')  + ')'
skewX.setParseAction( lambda t : SvgSkewX( t.angle ) )

skewY = 'skewY' + '(' + number('angle')  + ')'
skewY.setParseAction( lambda t : SvgSkewY( t.angle ) )

transform = matrix | translate | scale | rotate | skewX | skewY

transformList = transform + ZeroOrMore( commaWsp + transform )

style = Dict( ZeroOrMore( Group( Word( srange('[a-zA-Z-]') ) + Suppress(':') + Word( srange('[0-9a-zA-z#.\'()-]') )  + Optional(Suppress(';') )) ) )

'''pyparsing is nice to read but this function speeds up the parsing by factor of 70 times!!'''
def parsePathCommand(s):
    res = []
    els = s.split()
    def isCommand(s):
        return s in 'MmZzLlHhVvCcSsQqTtAa'
    while len(els) > 0 and isCommand(els[0]):
        cmd = [els[0]]
        els = els[1:]
        while len(els) > 0 and not isCommand(els[0]):
            flts = els[0].split(',')
            for f in flts:
                cmd.append( float(f))
            els = els[1:]
        res.append(cmd)
    return res

''' A list of the specific shape elements we currently support'''
shapeElements = [ 
          '{http://www.w3.org/2000/svg}g',
          '{http://www.w3.org/2000/svg}rect',
          '{http://www.w3.org/2000/svg}path' 
          ]

''' 
Every node derives from this base class.
Once a new node has been defined it is registered with the
base class via registerTagParser this will route the parsing
appropriately according to declared QName.
'''
class SvgNode(object):
    tagParsers = {}
    
    @classmethod
    def registerTagParser(cls,name,cls_):
        cls.tagParsers[name] = cls_
        
    def __init__(self,root):
        self.children = []
        self.id = self.readAttr(root,'id')
        
    def addChild(self,child):
        self.children.append(child)
        
    def parseSubElements( self, root, tags):
        for el in root:
            if el.tag in tags:
                if self.tagParsers.has_key( el.tag ):
                    self.addChild( self.tagParsers[ el.tag ]( el ) )
                else:
                    raise "Unimplemented: " + el.tag
                
    def readAttr(self,el,attr):
        if el.attrib.has_key(attr):
            return el.attrib[attr]
        else:
            return None
    
    def parseAttr(self,parser,el,attr,strip=True,):
        a = self.readAttr( el, attr )
        if not a is None:
            res = parser.parseString(a)
            if len(res.keys()) > 0:
                return res.asDict()
            res = res.asList()
            if len(res) == 1 and strip:
                return res[0]
            else:
                return res
        else:
            return None
        
    def dumpChildren(self,indent):
        s = ''
        for c in self.children:
            s += c.dump( indent )
        return s
    
    def dump(self,indent):
        return indent * ' ' + 'SvgNode\n' + self.dumpChildren(indent+1)
    
    def __repr__(self):
        return self.dump(0)
    
    def render(self, renderer):
        for c in self.children:
            c.render(renderer)

class SvgRect(SvgNode):
    def __init__(self,root):
        super(SvgRect,self).__init__(root)
        self.transform = self.parseAttr(transformList,root,'transform')
        self.width = self.parseAttr( number, root,'width')
        self.height = self.parseAttr( number, root, 'height')
        self.rx = self.parseAttr( number, root, 'rx')
        self.ry = self.parseAttr( number, root, 'ry')
        self.x = self.parseAttr( number, root, 'x')
        self.y = self.parseAttr( number, root, 'y')
        self.style = self.parseAttr( style, root, 'style')
        if self.rx is None:
            self.rx = 0.0
        if self.ry is None:
            self.ry = 0.0

    def render(self, renderer):
        renderer.enterGroup(self.transform)
        renderer.setStyle( self.style )
        if self.rx == 0.0 and self.ry == 0.0:
            renderer.rectangle(self.x,self.y,self.width,self.height)
        else:
            renderer.roundedRectangle(self.x,self.y,self.width,self.height,self.rx,self.ry)
        renderer.render()
        renderer.exitGroup()

    def dump(self,indent):
        return indent * ' ' + 'Rect %s width=%s height=%s rx=%s ry=%s x=%s y=%s style=%s\n'%(self.id, self.width, self.height, self.rx, self.ry, self.x, self.y, self.style)  + self.dumpChildren(indent+1)

SvgNode.registerTagParser('{http://www.w3.org/2000/svg}rect', SvgRect) 

class SvgPath(SvgNode):
    def __init__(self,root):
        super(SvgPath,self).__init__(root)
        self.d = parsePathCommand( self.readAttr(root,'d') )
        self.transform = self.parseAttr(transformList,root,'transform')
        self.style = self.parseAttr(style, root,'style')

    def render(self, renderer):
        renderer.enterGroup(self.transform)
        renderer.setStyle( self.style )
                    
        def cluster(lst,n):
                return zip(*[iter(lst)]*n)
            
        for e in self.d:

            cmd = e[0].lower()
            rel = e[0].islower()

            # Move to command
            if cmd == 'm':
                renderer.move( rel, e[1], e[2])
                map( lambda (x, y) : renderer.line(rel, x, y), cluster(e[3:],2) )
                
            # Close path command
            elif cmd == 'z':
                renderer.closePath()
                
            # Line to commands
            elif cmd == 'l':
                map( lambda (x, y) : renderer.line(rel, x, y), cluster(e[1:],2) )
            elif cmd == 'h':
                if not rel:
                    ( cx, cy ) = renderer.getCurrentPoint()
                    map( lambda x : renderer.line(False, x, cy), e[1:] )
                else:
                    map( lambda x : renderer.line(True, x, 0), e[1:] )
            elif cmd == 'v':
                if not rel:
                    ( cx, cy ) = renderer.getCurrentPoint()
                    map( lambda y : renderer.line(False, cx, y ), e[1:] )
                else:
                    map( lambda y : renderer.line(True, 0,y ), e[1:] )
                    
            # Cubic bezier
            elif cmd == 'c':
                map( lambda (x1, y1, x2, y2, x, y ) : renderer.curve(rel, x1, y1, x2, y2, x, y), cluster(e[1:],6) )
            elif cmd == 's':
                pass            # TODO: Implement this
            # Quadratic bezier
            elif cmd == 'q':
                pass            # TODO: Implement this
            elif cmd == 't':
                pass            # TODO: Implement this
            # Elliptical arc
            elif cmd == 'a':
                pass            # TODO: Implement this
        renderer.render()
        renderer.exitGroup()
        
    def dump(self,indent):
        return indent * ' ' + 'Path %s transform=%s style=%s d=%s\n'%(self.id, self.transform, self.style, self.d) + self.dumpChildren(indent+1)

SvgNode.registerTagParser('{http://www.w3.org/2000/svg}path', SvgPath) 

class SvgGroup(SvgNode):
    def __init__(self,root):
        super(SvgGroup,self).__init__(root)
        self.transform = self.parseAttr(transformList,root,'transform')
        self.parseSubElements( root,shapeElements)
        
    def render(self, renderer):
        renderer.enterGroup( self.transform )
        super(SvgGroup,self).render(renderer)
        renderer.exitGroup()

    def dump(self,indent):
        return indent * ' ' + 'Group %s'%self.id + ' transform=' + str(self.transform)+ '\n' + self.dumpChildren(indent+1) 

SvgNode.registerTagParser('{http://www.w3.org/2000/svg}g', SvgGroup) 

class Svg(SvgNode):
    def __init__(self,root):
        super(Svg,self).__init__(root)
        self.parseSubElements( root,shapeElements)

    def dump(self,indent):
        return indent * ' ' + 'Svg %s\n'%self.id + self.dumpChildren(indent+1)

SvgNode.registerTagParser('{http://www.w3.org/2000/svg}svg', Svg)