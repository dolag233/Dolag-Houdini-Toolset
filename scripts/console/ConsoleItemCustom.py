"""
    User custom console items
"""
import hou
from ConsoleItem import ConsoleItem
from Dolag import utils as du

# CUSTOM_ITEMS contains all user customized console item here
# you can simply create ConsoleItem object and append to CUSTOM_ITEMS
CUSTOM_ITEMS = []


# create callback for custom item
# context are defined in ConsoleContext.py
def my_custom_0_cb(context):
    if context["selected_nodes"]:
        msg = "You don't select any node"
        if len(context["selected_nodes"]) > 1:
            msg = "You select " + str(len(context["selected_nodes"])) + " Nodes"
        elif len(context["selected_nodes"]) == 1:
            msg = "You select 1 Node"

        hou.ui.displayMessage(msg)


# create custom item
my_custom_0 = ConsoleItem(item_name="Count Node", alias="cn", callback=my_custom_0_cb)
CUSTOM_ITEMS.append(my_custom_0)


# open parm tab
def create_parmsheet_cb(context):
    desktop = hou.ui.curDesktop()
    pane = desktop.createFloatingPane(hou.paneTabType.Parm)
    if len(context["selected_nodes"]) != 0:
        pane.setCurrentNode(context["selected_nodes"][0])


create_parmsheet = ConsoleItem(item_name="Open Spreadsheet", alias="", callback=create_parmsheet_cb)
CUSTOM_ITEMS.append(create_parmsheet)


# open scene view
def create_sceneview_cb(context):
    desktop = hou.ui.curDesktop()
    pane = desktop.createFloatingPane(hou.paneTabType.SceneView)


create_sceneview = ConsoleItem(item_name="Open Scene View", alias="sv", callback=create_sceneview_cb)
CUSTOM_ITEMS.append(create_sceneview)


# open detail pane
def create_detail_pane_cb(context):
    desktop = hou.ui.curDesktop()
    pane = desktop.createFloatingPane(hou.paneTabType.DetailsView)
    if len(context["selected_nodes"]) != 0:
        pane.setCurrentNode(context["selected_nodes"][0])


create_detail_pane = ConsoleItem(item_name="Open Param Info Pane", alias="par", callback=create_detail_pane_cb)
CUSTOM_ITEMS.append(create_detail_pane)


# open detail pane
def create_help_browser_cb(context):
    desktop = hou.ui.curDesktop()
    desktop.createFloatingPane(hou.paneTabType.HelpBrowser)


create_help_browser = ConsoleItem(item_name="Open Cookbook", alias="cb", callback=create_help_browser_cb)
CUSTOM_ITEMS.append(create_help_browser)


# open python shell
def create_python_shell_cb(context):
    desktop = hou.ui.curDesktop()
    desktop.createFloatingPane(hou.paneTabType.PythonShell)


create_python_shell = ConsoleItem(item_name="Open Python Shell", alias="ps", callback=create_python_shell_cb)
CUSTOM_ITEMS.append(create_python_shell)


# copy node path
def copy_node_path_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        du.writeClipboard(nodes[0].path())


create_python_shell = ConsoleItem(item_name="Copy Node Path", alias="np", callback=copy_node_path_cb)
CUSTOM_ITEMS.append(create_python_shell)
