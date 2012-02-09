# see http://www.w3.org/TR/SVG/
#
# This is a somewhat incomplete and minimalistic SVG parser
# that can render to a pycairo context which should be adequate
# for most needs.
#
# It purpose is to create a way of rendering vector graphics easily
# in Python rather than being a general purposes SVG renderer.
#
# i.e. the SVG files are tailored to work with this parser.
#
# TODO: No reason why this can't be made a compliant SVG
# implementation, just needs the effort :-)
#
# Implementation is via xml.etree.ElementTree and the
# pyparsing declarative EBNF based string parser.
#

import xml.etree.ElementTree as ET
from pyparsing import Word, Optional, CaselessLiteral, nums, oneOf, Combine, ZeroOrMore, srange, Dict, Suppress, Group, OneOrMore #@UnresolvedImport
import math

# FIXME: The number rule might be more efficiently implemented as a regex.
# performance testing needed against both implementations.

commaWsp = Optional(',').suppress()

digitSequence = Word( nums )

sign = oneOf( '+ -' )

integerConstant = digitSequence

fractionalConstant = digitSequence + Optional( '.' +  digitSequence ) | '.' +  digitSequence 

exponent = oneOf( 'e E' ) + Optional( sign ) + digitSequence

def parseFloat( t):
    return float( t[0] ) 
number = Combine( Optional( sign ) + fractionalConstant + Optional( exponent ) )
number.setParseAction( parseFloat)

angle = number + ( CaselessLiteral('deg') | CaselessLiteral('grad') | CaselessLiteral('rad') )

class SvgTransform(object):
    pass

class SvgMatrix(SvgTransform):
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

class SvgTranslate(SvgTransform):
    def __init__(self, tx, ty):
        self.tx = tx
        self.ty = ty
    def __eq__(a,b): #@NoSelf
        return a.tx == b.tx and b.ty == b.ty
    def __repr__(self):
        return 'translate(' + str(self.tx) + ',' + str(self.ty) + ')'
    
class SvgScale(SvgTransform):
    def __init__(self, sx, sy):
        self.sx = sx
        self.sy = sy
    def __eq__(a,b): #@NoSelf
        return a.sx == b.sx and b.sy == b.sy
    def __repr__(self):
        return 'scale(' + str(self.sx) + ',' + str(self.sy) + ')'
    
class SvgRotate(SvgTransform):
    def __init__(self, angle, cx, cy):
        self.angle = angle
        self.cx = cx
        self.cy = cy
    def __eq__(a,b): #@NoSelf
        return a.cx == b.cx and b.cy == b.cy and a.angle == b.angle
    def __repr__(self):
        return 'rotate(' + str(self.angle) + ',' + str(self.cx) + ',' + str(self.cy) + ')'

class SvgSkewX(SvgTransform):
    def __init__(self, angle ):
        self.angle = angle
    def __eq__(a,b): #@NoSelf
        return a.angle == b.angle
    def __repr__(self):
        return 'skewX(' + str(self.angle) + ')'
    
class SvgSkewY(SvgTransform):
    def __init__(self, angle ):
        self.angle = angle
    def __eq__(a,b): #@NoSelf
        return a.angle == b.angle
    def __repr__(self):
        return 'skewY(' + str(self.angle) + ')'

matrix = 'matrix' + '(' + number('a') + commaWsp \
                + number('b') + commaWsp \
                + number('c') + commaWsp \
                + number('d') + commaWsp \
                + number('e') + commaWsp \
                + number('f') + ')'
matrix.setParseAction( lambda t : SvgMatrix( t.a, t.b, t.c, t.d, t.e, t.f ) )

translate = 'translate' + '(' + number('tx') + commaWsp + Optional( number('ty') ) + ')'
translate.setParseAction( lambda t : SvgTranslate( t.tx, t.ty ) )

scale = 'scale' + '(' + number('sx')  + commaWsp + Optional( number.setName('sy') )  + ')'
scale.setParseAction( lambda t : SvgScale( t.sx, t.sy ) )

rotate = 'rotate' + '(' + number('angle') + Optional( commaWsp + number('cx') + commaWsp + number('cy')  ) + ')'
rotate.setParseAction( lambda t : SvgRotate( t.angle, t.cx, t.cy ) )

skewX = 'skewX' + '(' + number('angle')  + ')'
skewX.setParseAction( lambda t : SvgSkewX( t.angle ) )

skewY = 'skewY' + '(' + number('angle')  + ')'
skewY.setParseAction( lambda t : SvgSkewY( t.angle ) )

transform = matrix | translate | scale | rotate | skewX | skewY

transformList = transform + ZeroOrMore( commaWsp + transform )

style = Dict( ZeroOrMore( Group( Word( srange('[a-zA-Z-]') ) + Suppress(':') + Word( srange('[0-9a-zA-z#.\'()]') )  + Optional(Suppress(';') )) ) )

pathCommand = Group( oneOf('M m')('command') + OneOrMore( number('x') + commaWsp + number('y') ) \
    |  oneOf( 'Z z' )('command') \
    |  oneOf( 'L l' )('command') + OneOrMore( number('x') + commaWsp + number('y') ) \
    |  oneOf( 'H h' )('command') + OneOrMore( number('x') ) \
    |  oneOf( 'V v' )('command') + OneOrMore( number('y') ) \
    |  oneOf( 'C c' )('command') + OneOrMore( number('x1') + commaWsp + number('y1') + commaWsp + number('x2') + commaWsp + number('y2') + commaWsp + number('x') + commaWsp + number('y') ) \
    |  oneOf( 'S s' )('command') + OneOrMore( number('x2') + commaWsp + number('y2') + commaWsp + number('x') + commaWsp +  number('y') ) \
    |  oneOf( 'Q q' )('command') + OneOrMore( number('x1') + commaWsp + number('y1') + commaWsp + number('x') + commaWsp + number('y') ) \
    |  oneOf( 'T t' )('command') + OneOrMore( number('x') + commaWsp + number('y') ) \
    |  oneOf( 'A a' )('command') + OneOrMore( number('rx') +commaWsp + number('ry') + commaWsp + number('x-axis-rotation')  + commaWsp + number('large-arc-flag') + commaWsp + number('sweep-flag') + commaWsp + number('x') + commaWsp + number('y') ) \
    )

path = OneOrMore( pathCommand )

shapeElements = [ 
          '{http://www.w3.org/2000/svg}g',
          '{http://www.w3.org/2000/svg}rect',
          '{http://www.w3.org/2000/svg}path' 
          ]

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
    
    def parseAttr(self,parser,el,attr):
        a = self.readAttr( el, attr )
        if not a is None:
            res = parser.parseString(a)
            if len(res.keys()) > 0:
                return res.asDict()
            res = res.asList()
            if len(res) == 1:
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
    
    def renderToCairo(self, cx):
        for c in self.children:
            c.renderToCairo(cx)

class SvgRect(SvgNode):
    def __init__(self,root):
        super(SvgRect,self).__init__(root)
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
        
    # Cairo doesn't have a native ellipse arc
    # so we have to construct one using transforms
    def renderEllArc(self,cx,w,h,s,e):
        ( sx, sy ) = cx.get_current_point()
        cx.save()
        cx.new_sub_path()
        cx.translate(sx,sy)
        cx.scale(1.0,-h/w)
        cx.arc(0.,0.,w,s,e)
        cx.restore()

    def renderToCairo(self, cx):
        if self.rx == 0.0 and self.ry == 0.0:
            # Simple rectangle
            cx.rectangle(self.x,self.y,self.width,self.height)
            cx.stroke()
        else:
            # Rounded rectangle needs to be constructed from
            # lines and ellipse arcs.
            cx.move_to( self.x + self.rx, self.y)
            cx.line_to( self.x + self.width - self.rx, self.y )
            cx.rel_move_to( 0, self.ry )
            self.renderEllArc( cx, self.rx, self.ry, 0.0, math.pi/2.0 )
            cx.rel_move_to( self.rx, self.ry )
            cx.rel_line_to( 0, self.height - 2*self.ry )
            cx.rel_move_to( -self.rx, 0 )
            self.renderEllArc( cx, self.rx, self.ry, 3*math.pi/2.0, 0.0  )
            cx.rel_move_to( -self.rx, self.ry )
            cx.rel_line_to( -(self.width - 2*self.rx), 0 )
            cx.rel_move_to( 0, -self.ry)
            self.renderEllArc( cx, self.rx, self.ry, math.pi, 3*math.pi/2.0 )
            cx.rel_move_to( -self.rx, -self.ry )
            cx.rel_line_to( 0, -(self.height - 2*self.ry))
            cx.rel_move_to( self.rx, 0 )
            self.renderEllArc(  cx, self.rx, self.ry, math.pi/2.0, math.pi )
            cx.rel_move_to( self.rx, -self.ry )
            cx.close_path()
            cx.stroke()
    
    def dump(self,indent):
        return indent * ' ' + 'Rect %s width=%s height=%s rx=%s ry=%s x=%s y=%s style=%s\n'%(self.id, self.width, self.height, self.rx, self.ry, self.x, self.y, self.style)  + self.dumpChildren(indent+1)

SvgNode.registerTagParser('{http://www.w3.org/2000/svg}rect', SvgRect) 

class SvgPath(SvgNode):
    def __init__(self,root):
        super(SvgPath,self).__init__(root)
        self.d = self.parseAttr(path, root,'d')
        self.transform = self.parseAttr(transformList,root,'transform')
        self.style = self.parseAttr(style, root,'style')
    
    def dump(self,indent):
        return indent * ' ' + 'Path %s transform=%s style=%s d=%s\n'%(self.id, self.transform, self.style, self.d) + self.dumpChildren(indent+1)

SvgNode.registerTagParser('{http://www.w3.org/2000/svg}path', SvgPath) 

class SvgGroup(SvgNode):
    def __init__(self,root):
        super(SvgGroup,self).__init__(root)
        self.transform = self.parseAttr(transformList,root,'transform')
        self.parseSubElements( root,shapeElements)

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

def loadSvgFile(fileName):
    return Svg( ET.parse(fileName).getroot() )