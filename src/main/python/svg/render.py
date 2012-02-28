import math
import cairo

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

class SvgCairoRenderer(SvgRenderer):
    
    def __init__(self,context):
        self._ctx = context
        self._strokeColor = None
        self._fillColor = None
    
    def parseColorValue(self,value):
        if value[0] == '#':
            return ( int(value[1:2],16), int(value[3:4],16), int(value[5:6],16) )
        else:
            #print "Warning: Unable to parse color: " + repr(value)
            return ( 0, 0 , 0 )
        
    def enterGroup(self,matrix):
        self._ctx.save()
        if not matrix is None: 
                self._ctx.transform( cairo.Matrix( matrix.a, matrix.b, matrix.c, matrix.d, matrix.e, matrix.f ) )
        
    def exitGroup(self):
        self._ctx.restore()
        
    def setStyle(self, styles):
        self._strokeColor = None
        self._fillColor  = None
        for (name,value) in styles.items():
            if name == 'stroke' and value != 'none':
                self._strokeColor = self.parseColorValue( value )
            elif name == 'fill' and value != 'none':
                self._fillColor = self.parseColorValue( value )
            elif name == 'stroke-width':
                self._strokeWidth = float( value )
    
    def _hasStroke(self):
        return self._strokeColor != None
    
    def _hasFill(self):
        return self._fillColor != None
    
    def _doStroke(self, preserve):
        self._ctx.set_source_rgb( self._strokeColor[0], self._strokeColor[1], self._strokeColor[2] )
        self._ctx.set_line_width( self._strokeWidth)
        if preserve:
            self._ctx.stroke_preserve()
        else:
            self._ctx.stroke()
    
    def _doFill(self, preserve):
        self._ctx.set_source_rgb( self._fillColor[0], self._fillColor[1], self._fillColor[2] )
        if preserve:
            self._ctx.fill_preserve()
        else:
            self._ctx.fill()
    
    def render(self):
        if self._hasStroke() and self._hasFill():
            self._doStroke( True )
            self._doFill( False )
        elif self._hasStroke():
            self._doStroke( False )
        elif self._hasFill():
            self._doFill( False )
    
    # Cairo doesn't have a native elliptical arc, but it's easy to 
    # construct one:
    def _ellipticalArc(self,sx,sy,w,h,s,e):
        self._ctx.scale(1.0,h/w)
        self._ctx.arc(sx,sy*w/h,w,s,e)
        self._ctx.scale(1.0,w/h)
        
    def rectangle(self, x, y, width, height):
        self._ctx.rectangle(x,y,width,height)
        
    def roundedRectangle(self, x, y, width, height, rx, ry ):
        # Rounded rectangle needs to be constructed from
        # lines and elliptical arcs.
        self._ctx.move_to( x + rx, y)
        self._ellipticalArc( x + width - rx, y + ry, rx, ry, 3*math.pi/2, 0 )
        self._ellipticalArc( x + width - rx, y + height - ry, rx, ry, 0, math.pi/2 )
        self._ellipticalArc( x + rx, y + height - ry, rx, ry, math.pi/2, math.pi )
        self._ellipticalArc( x + rx, y + ry, rx, ry, math.pi, math.pi/2.0 )
        self._ctx.close_path()
        
    def getCurrentPoint(self):
        return self._ctx.get_current_point()
    
    def hasCurrentPoint(self):
        return self._ctx.has_current_point()

    def move(self, rel, x, y ):
        if rel and self.hasCurrentPoint():
            self._ctx.rel_move_to( x, y)
        else:
            self._ctx.move_to( x, y )
    
    def line(self, rel, x, y):
        if rel:
            self._ctx.rel_line_to(x,y)
        else:
            self._ctx.line_to(x,y)
            
    def closePath(self):
        self._ctx.close_path()

    def curve(self,rel,x1,y1,x2,y2,x3,y3):
        if rel:
            self._ctx.rel_curve_to(x1,y1,x2,y2,x3,y3)
        else:
            self._ctx.curve_to(x1,y1,x2,y2,x3,y3)