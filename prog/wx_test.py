# coding:utf-8
import wx

application = wx.App()

frame = wx.frame(None, wx.ID_ANY, u"テストフレーム")
frame.Show()

application.MainLoop()
