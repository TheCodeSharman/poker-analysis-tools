import wx

class Replayer(wx.Frame):
    """ We simply derive a new class of Frame. """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(200, 100))
        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.Show(True)
    

if __name__ == '__main__':
    app = wx.App(False)
    frame = Replayer(None, 'Replayer')
    app.MainLoop()