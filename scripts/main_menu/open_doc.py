# coding=utf-8
"""
    visit doc in inhouse browser
"""
import hou
import webbrowser

desk = hou.ui.curDesktop()
browser = desk.createFloatingPane(hou.paneTabType.HelpBrowser)
browser.setUrl("http://www.vis.dolag.work/houdini-toolset/简介.html")
