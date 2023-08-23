"""
    User custom console items
"""
import hou
import platform
from utils.open_vex_in_vsc import openVexInVSC


if platform.python_version_tuple()[0] == '2':
    from ConsoleItem import ConsoleItem

elif platform.python_version_tuple()[0] == '3':
    from .ConsoleItem import ConsoleItem

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


# create node(s) reference(s)
def create_node_ref_cb(context):
    from scripts.op_menu.node_ref import dupNodeRef
    nodes = context["selected_nodes"]
    if nodes:
        for node in nodes:
            dupNodeRef(node)


create_python_shell = ConsoleItem(item_name="Create Node Reference", alias="ref", callback=create_node_ref_cb)
CUSTOM_ITEMS.append(create_python_shell)


# display points
def display_point_cb(context):
    import hou
    # Get a reference to the geometry viewer
    pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.SceneViewer)

    # Get the display settings
    settings = pane.curViewport().settings()

    # Get display mode
    display_mode = settings.displaySet(hou.displaySetType.DisplayModel)

    # switch point marker
    display_mode.showPointMarkers(not display_mode.isShowingPointMarkers())


create_python_shell = ConsoleItem(item_name="Display Point Markers", alias="dp", callback=display_point_cb)
CUSTOM_ITEMS.append(create_python_shell)

# display point normals
def display_point_normal_cb(context):
    import hou
    # Get a reference to the geometry viewer
    pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.SceneViewer)

    # Get the display settings
    settings = pane.curViewport().settings()

    # Get display mode
    display_mode = settings.displaySet(hou.displaySetType.DisplayModel)

    # switch point normals
    display_mode.showPointNormals(not display_mode.isShowingPointNormals())

    # display point markers
    if display_mode.isShowingPointNormals():
        display_mode.showPointMarkers(True)


create_python_shell = ConsoleItem(item_name="Display Point Normals", alias="dpn", callback=display_point_normal_cb)
CUSTOM_ITEMS.append(create_python_shell)

# display point numbers
def display_point_number_cb(context):
    import hou
    # Get a reference to the geometry viewer
    pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.SceneViewer)

    # Get the display settings
    settings = pane.curViewport().settings()

    # Get display mode
    display_mode = settings.displaySet(hou.displaySetType.DisplayModel)

    # switch point numbers
    display_mode.showPointNumbers(not display_mode.isShowingPointNumbers())

    # display point markers
    if display_mode.isShowingPointNumbers():
        display_mode.showPointMarkers(True)


create_python_shell = ConsoleItem(item_name="Display Point Numbers", alias="dpn", callback=display_point_number_cb)
CUSTOM_ITEMS.append(create_python_shell)


# display prim normals
def display_prim_normal_cb(context):
    import hou
    # Get a reference to the geometry viewer
    pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.SceneViewer)

    # Get the display settings
    settings = pane.curViewport().settings()

    # Get display mode
    display_mode = settings.displaySet(hou.displaySetType.DisplayModel)

    # switch prim normals
    display_mode.showPrimNormals(not display_mode.isShowingPrimNormals())


create_python_shell = ConsoleItem(item_name="Display Prim Normals", alias="dpn", callback=display_prim_normal_cb)
CUSTOM_ITEMS.append(create_python_shell)

# edit wrangle or python with vsc
def code_with_vsc_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        for node in nodes:
            if isinstance(node, hou.SopNode):
                parms = node.parms()
                code = [v for v in parms if v.name() == "snippet" or v.name == "python"]
                if len(code) > 0:
                    for v in code:
                        openVexInVSC(v.unexpandedString())


create_python_shell = ConsoleItem(item_name="Edit Code in VSC", alias="vex", callback=code_with_vsc_cb)
CUSTOM_ITEMS.append(create_python_shell)

from op_menu import set_preset_style

# preset input node style
def set_preset_node_style_input_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        for node in nodes:
            set_preset_style.setNodePresetStyle(node, "input")


create_python_shell = ConsoleItem(item_name="Set Input Node Style", alias="input", callback=set_preset_node_style_input_cb)
CUSTOM_ITEMS.append(create_python_shell)

# preset output node style
def set_preset_node_style_output_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        for node in nodes:
            set_preset_style.setNodePresetStyle(node, "output")


create_python_shell = ConsoleItem(item_name="Set Output Node Style", alias="output", callback=set_preset_node_style_output_cb)
CUSTOM_ITEMS.append(create_python_shell)

# preset global control node style
def set_preset_node_style_global_control_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        for node in nodes:
            set_preset_style.setNodePresetStyle(node, "global control")


create_python_shell = ConsoleItem(item_name="Set Global Control Node Style", alias="global control", callback=set_preset_node_style_global_control_cb)
CUSTOM_ITEMS.append(create_python_shell)

# preset output node style
def set_preset_node_style_heavy_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        for node in nodes:
            set_preset_style.setNodePresetStyle(node, "heavy")


create_python_shell = ConsoleItem(item_name="Set Heavy Node Style", alias="heavy", callback=set_preset_node_style_heavy_cb)
CUSTOM_ITEMS.append(create_python_shell)

# preset important node style
def set_preset_node_style_important_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        for node in nodes:
            set_preset_style.setNodePresetStyle(node, "important")


create_python_shell = ConsoleItem(item_name="Set Important Node Style", alias="important", callback=set_preset_node_style_important_cb)
CUSTOM_ITEMS.append(create_python_shell)

# preset milestone node style
def set_preset_node_style_milestone_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        for node in nodes:
            set_preset_style.setNodePresetStyle(node, "milestone")


create_python_shell = ConsoleItem(item_name="Set Milestone Node Style", alias="milestone", callback=set_preset_node_style_milestone_cb)
CUSTOM_ITEMS.append(create_python_shell)