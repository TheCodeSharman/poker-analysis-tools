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

class SvgCairoRenderer(SvgRenderer):
    
    def __init__(self,context):
        self._ctx = context
        self._strokeColor = None
        self._fillColor = None
    
    def parseColorValue(self,value):
        if value[0] == '#':
            return ( int(value[1:2],16), int(value[3:4],16), int(value[5:6],16) )
        else:
            raise "Unable to parse color"
        
    def enterGroup(self,matrix):
        self._ctx.save()
        if not matrix is None: 
                self._ctx.transform( cairo.Matrix( matrix.a, matrix.b, matrix.c, matrix.d, matrix.e, matrix.f ) )
        
    def exitGroup(self):
        self._ctx.restore()
        
    def setStyle(self, styles):
        for (name,value) in styles.items():
            if name == 'stroke':
                if value != 'none':
                    self._strokeColor = self.parseColorValue( value )
                else:
                    self._strokeColor = None
            elif name == 'fill':
                if value != 'none':
                    self._fillColor = self.parseColorValue( value )
                else:
                    self._fillColor  = None
            elif name == 'stroke-width':
                    self._strokeWidth = float( value )
    
    def hasStroke(self):
        return self._strokeColor != None
    
    def hasFill(self):
        return self._fillColor != None
    
    def doStroke(self, preserve):
        self._ctx.set_source_rgb( self._strokeColor[0], self._strokeColor[1], self._strokeColor[2] )
        self._ctx.set_line_width( self._strokeWidth)
        if preserve:
            self._ctx.stroke_preserve()
        else:
            self._ctx.stroke()
    
    def doFill(self, preserve):
        self._ctx.set_source_rgb( self._fillColor[0], self._fillColor[1], self._fillColor[2] )
        if preserve:
            self._ctx.fill_preserve()
        else:
            self._ctx.fill()
    
    def doRender(self):
        if self.hasStroke() and self.hasFill():
            self.doStroke( True )
            self.doFill( False )
        elif self.hasStroke():
            self.doStroke( False )
        elif self.hasFill():
            self.doFill( False )
    
    # Cairo doesn't have a native elliptical arc, but it's easy to 
    # construct one:
    def _ellipticalArc(self,sx,sy,w,h,s,e):
        self._ctx.scale(1.0,-h/w)
        self._ctx.arc_negative(sx,sy*-w/h,w,s,e)
        self._ctx.scale(1.0,-w/h)
        
    def rectangle(self, x, y, width, height):
        # Simple rectangle
        self._ctx.rectangle(x,y,width,height)
        self.doRender()
        
    def roundedRectangle(self, x, y, width, height, rx, ry ):
        # Rounded rectangle needs to be constructed from
        # lines and elliptical arcs.
        self._ctx.move_to( x + rx, y)
        self._ellipticalArc( x + width - rx, y + ry, rx, ry, math.pi/2.0, 0.0 )
        self._ellipticalArc( x + width - rx, y + height - ry, rx, ry, 0.0, 3*math.pi/2.0  )
        self._ellipticalArc( x + rx, y + height - ry, rx, ry, 3*math.pi/2.0, math.pi )
        self._ellipticalArc( x + rx, y + ry, rx, ry, math.pi, math.pi/2.0 )
        self._ctx.close_path()
        self.doRender()
