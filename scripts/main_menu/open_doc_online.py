"""
    visit doc online
"""
import hou
import webbrowser

desk = hou.ui.curDesktop()
browser = desk.createFloatingPane(hou.paneTabType.HelpBrowser)
browser.setUrl("http://www.vis.dolag.work/houdini-toolset/")
