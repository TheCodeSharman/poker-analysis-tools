import wx
import wx.lib.wxcairo
import cairo
import svg.parse
import svg.render

import cProfile
 
class PokerTable(wx.Window):
    def __init__(self, parent):
        wx.Window.__init__(self, parent)
        self.tableSvg = svg.parse.loadSvgFile("resources/cards.svg")
        #print self.tableSvg
        self.InitBuffer()
        self.Bind(wx.EVT_SIZE, self.OnSize) 
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def InitBuffer(self):
        w, h = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(w,h)
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        self.DrawTable(dc)
        
    def DrawTable(self,dc):
        context = wx.lib.wxcairo.ContextFromDC(dc)
        self.tableSvg.render(svg.render.SvgCairoRenderer(context))
        
    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self, self.buffer)
        
    def OnSize(self, evt):
        self.InitBuffer()

        
class Replayer(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(640, 400))
        self.control = PokerTable(self)
        self.Show(True)
        

def main():
    app = wx.App(False)
    frame = Replayer(None, 'Replayer')
    app.MainLoop()
    
if __name__ == '__main__':
    main() # cProfile.run('main()', 'profile')
