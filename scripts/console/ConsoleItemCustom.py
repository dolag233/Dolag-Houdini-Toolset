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

CUSTOM_ITEMS = []


def my_custom_0_cb(context):
    if context["selected_nodes"]:
        msg = "You don't select any node"
        if len(context["selected_nodes"]) > 1:
            msg = "You select " + str(len(context["selected_nodes"])) + " Nodes"
        elif len(context["selected_nodes"]) == 1:
            msg = "You select 1 Node"

        hou.ui.displayMessage(msg)


my_custom_0 = ConsoleItem(item_name="Count Node", alias="cn", callback=my_custom_0_cb)
CUSTOM_ITEMS.append(my_custom_0)


def create_parmsheet_cb(context):
    desktop = hou.ui.curDesktop()
    pane = desktop.createFloatingPane(hou.paneTabType.Parm)
    if len(context["selected_nodes"]) != 0:
        pane.setCurrentNode(context["selected_nodes"][0])


create_parmsheet = ConsoleItem(item_name="Open Spreadsheet", alias="", callback=create_parmsheet_cb)
CUSTOM_ITEMS.append(create_parmsheet)


def create_sceneview_cb(context):
    desktop = hou.ui.curDesktop()
    pane = desktop.createFloatingPane(hou.paneTabType.SceneView)


create_sceneview = ConsoleItem(item_name="Open Scene View", alias="sv", callback=create_sceneview_cb)
CUSTOM_ITEMS.append(create_sceneview)


def create_detail_pane_cb(context):
    desktop = hou.ui.curDesktop()
    pane = desktop.createFloatingPane(hou.paneTabType.DetailsView)
    if len(context["selected_nodes"]) != 0:
        pane.setCurrentNode(context["selected_nodes"][0])


create_detail_pane = ConsoleItem(item_name="Open Param Info Pane", alias="par", callback=create_detail_pane_cb)
CUSTOM_ITEMS.append(create_detail_pane)


def create_help_browser_cb(context):
    desktop = hou.ui.curDesktop()
    desktop.createFloatingPane(hou.paneTabType.HelpBrowser)


create_help_browser = ConsoleItem(item_name="Open Cookbook", alias="cb", callback=create_help_browser_cb)
CUSTOM_ITEMS.append(create_help_browser)


def create_python_shell_cb(context):
    desktop = hou.ui.curDesktop()
    desktop.createFloatingPane(hou.paneTabType.PythonShell)


create_python_shell = ConsoleItem(item_name="Open Python Shell", alias="ps", callback=create_python_shell_cb)
CUSTOM_ITEMS.append(create_python_shell)


def create_performance_monitor_cb(context):
    monitor = hou.ui.curDesktop().createFloatingPaneTab(hou.paneTabType.PerformanceMonitor)
    monitor.startRecording()


create_performance_monitor = ConsoleItem(item_name="Open Performance Monitor", alias="pm", callback=create_performance_monitor_cb)
CUSTOM_ITEMS.append(create_performance_monitor)


def copy_node_path_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        du.writeClipboard(nodes[0].path())


tmp_console_item = ConsoleItem(item_name="Copy Node Path", alias="np", callback=copy_node_path_cb)
CUSTOM_ITEMS.append(tmp_console_item)


def create_node_ref_cb(context):
    from scripts.op_menu.node_ref import dupNodeRef
    nodes = context["selected_nodes"]
    if nodes:
        for node in nodes:
            dupNodeRef(node)


tmp_console_item = ConsoleItem(item_name="Create Node Reference", alias="ref", callback=create_node_ref_cb)
CUSTOM_ITEMS.append(tmp_console_item)


def display_point_cb(context):
    import hou
    pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.SceneViewer)
    settings = pane.curViewport().settings()
    display_mode = settings.displaySet(hou.displaySetType.DisplayModel)
    display_mode.showPointMarkers(not display_mode.isShowingPointMarkers())


tmp_console_item = ConsoleItem(item_name="Display Point Markers", alias="dp", callback=display_point_cb)
CUSTOM_ITEMS.append(tmp_console_item)

def display_point_normal_cb(context):
    import hou
    pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.SceneViewer)
    settings = pane.curViewport().settings()
    display_mode = settings.displaySet(hou.displaySetType.DisplayModel)
    display_mode.showPointNormals(not display_mode.isShowingPointNormals())
    if display_mode.isShowingPointNormals():
        display_mode.showPointMarkers(True)


tmp_console_item = ConsoleItem(item_name="Display Point Normals", alias="dpn", callback=display_point_normal_cb)
CUSTOM_ITEMS.append(tmp_console_item)


def display_point_number_cb(context):
    import hou

    pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.SceneViewer)


    settings = pane.curViewport().settings()


    display_mode = settings.displaySet(hou.displaySetType.DisplayModel)

    # switch point numbers
    display_mode.showPointNumbers(not display_mode.isShowingPointNumbers())

    # display point markers
    if display_mode.isShowingPointNumbers():
        display_mode.showPointMarkers(True)


tmp_console_item = ConsoleItem(item_name="Display Point Numbers", alias="dpn", callback=display_point_number_cb)
CUSTOM_ITEMS.append(tmp_console_item)



def display_prim_normal_cb(context):
    import hou

    pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.SceneViewer)


    settings = pane.curViewport().settings()


    display_mode = settings.displaySet(hou.displaySetType.DisplayModel)

    # switch prim normals
    display_mode.showPrimNormals(not display_mode.isShowingPrimNormals())


tmp_console_item = ConsoleItem(item_name="Display Prim Normals", alias="dpn", callback=display_prim_normal_cb)
CUSTOM_ITEMS.append(tmp_console_item)

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


tmp_console_item = ConsoleItem(item_name="Edit Code in VSC", alias="vex", callback=code_with_vsc_cb)
CUSTOM_ITEMS.append(tmp_console_item)

from op_menu import set_preset_style


def set_preset_node_style_input_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        with hou.undos.group("Set Input Node Style"):
            for node in nodes:
                set_preset_style.setNodePresetStyle(node, "input")


tmp_console_item = ConsoleItem(item_name="Set Input Node Style", alias="input", callback=set_preset_node_style_input_cb)
CUSTOM_ITEMS.append(tmp_console_item)


def set_preset_node_style_output_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        with hou.undos.group("Set Output Node Style"):
            for node in nodes:
                set_preset_style.setNodePresetStyle(node, "output")


tmp_console_item = ConsoleItem(item_name="Set Output Node Style", alias="output", callback=set_preset_node_style_output_cb)
CUSTOM_ITEMS.append(tmp_console_item)

# preset global control node style
def set_preset_node_style_global_control_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        with hou.undos.group("Set Global Node Style"):
            for node in nodes:
                set_preset_style.setNodePresetStyle(node, "global control")


tmp_console_item = ConsoleItem(item_name="Set Global Control Node Style", alias="global control", callback=set_preset_node_style_global_control_cb)
CUSTOM_ITEMS.append(tmp_console_item)

# preset heavy node style
def set_preset_node_style_heavy_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        with hou.undos.group("Set Heavy Node Style"):
            for node in nodes:
                set_preset_style.setNodePresetStyle(node, "heavy")


tmp_console_item = ConsoleItem(item_name="Set Heavy Node Style", alias="heavy", callback=set_preset_node_style_heavy_cb)
CUSTOM_ITEMS.append(tmp_console_item)

# preset important node style
def set_preset_node_style_important_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        with hou.undos.group("Set Important Node Style"):
            for node in nodes:
                set_preset_style.setNodePresetStyle(node, "important")


tmp_console_item = ConsoleItem(item_name="Set Important Node Style", alias="important", callback=set_preset_node_style_important_cb)
CUSTOM_ITEMS.append(tmp_console_item)

# preset milestone node style
def set_preset_node_style_milestone_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        with hou.undos.group("Set Milestone Node Style"):
            for node in nodes:
                set_preset_style.setNodePresetStyle(node, "milestone")


tmp_console_item = ConsoleItem(item_name="Set Milestone Node Style", alias="milestone", callback=set_preset_node_style_milestone_cb)
CUSTOM_ITEMS.append(tmp_console_item)

# preset useless node style
def set_preset_node_style_useless_cb(context):
    nodes = context["selected_nodes"]
    if nodes:
        with hou.undos.group("Set Useless Node Style"):
            for node in nodes:
                set_preset_style.setNodePresetStyle(node, "useless")


tmp_console_item = ConsoleItem(item_name="Set Useless Node Style", alias="useless", callback=set_preset_node_style_useless_cb)
CUSTOM_ITEMS.append(tmp_console_item)

from op_menu.node_layout import verticalSpacingAllNodes, verticalSpacing, snapToGrid, snapToGridAllNodes

def vertical_spacing_cb(context):
    items = context["selected_items"]
    if len(items) == 0:
        verticalSpacingAllNodes(True)

    else:
        verticalSpacing(items, True)

    return


tmp_console_item = ConsoleItem(item_name="Layout Nodes", alias="layout", callback=vertical_spacing_cb)
CUSTOM_ITEMS.append(tmp_console_item)

def vertical_spacing_upward_cb(context):
    items = context["selected_items"]
    if len(items) == 0:
        verticalSpacingAllNodes()

    else:
        verticalSpacing(items)

    return


tmp_console_item = ConsoleItem(item_name="Layout Nodes Downward", alias="layoutd", callback=vertical_spacing_upward_cb)
CUSTOM_ITEMS.append(tmp_console_item)

from op_menu.node_layout import verticalCompressingAllNodes, verticalCompressing
# vertical compressing all nodes
def vertical_compressing_cb(context):
    items = context["selected_items"]
    if len(items) == 0:
        verticalCompressingAllNodes(True)

    else:
        verticalCompressing(items, True)

    return


tmp_console_item = ConsoleItem(item_name="Compress Node Space", alias="compress", callback=vertical_compressing_cb)
CUSTOM_ITEMS.append(tmp_console_item)

# vertical compressing all nodes upward
def vertical_compressing_upward_cb(context):
    items = context["selected_items"]
    if len(items) == 0:
        verticalCompressingAllNodes()

    else:
        verticalCompressing(items)

    return


tmp_console_item = ConsoleItem(item_name="Compress Node Space Downward", alias="compressd", callback=vertical_compressing_upward_cb)
CUSTOM_ITEMS.append(tmp_console_item)

from op_menu.wire_hub import wireHub, wireHubs

def wire_hub_cb(context):
    items = context["selected_items"]
    if len(items) == 0:
        return

    elif len(items) == 1:
        wireHub(items[0])

    else:
        wireHubs(items)

tmp_console_item = ConsoleItem(item_name="Organize Wires", alias="wire", callback=wire_hub_cb)
CUSTOM_ITEMS.append(tmp_console_item)

def auto_resize_networkbox_cb(context):
    items = context["selected_items"]
    with hou.undos.group("Resize Network Boxes"):
        for i in items:
            if isinstance(i, hou.NetworkBox):
                i.fitAroundContents()

tmp_console_item = ConsoleItem(item_name="Network Box Auto Resize", alias="resize", callback=auto_resize_networkbox_cb)
CUSTOM_ITEMS.append(tmp_console_item)


# chatgpt
from main_menu import chatgpt_UI
from utils import show_UI
from PySide2 import QtCore
def chatgpt_cb(context):
    if "dolag::houdini_master_AI_console" in hou.pypanel.interfaces().keys():
        cursor_pos = context["screen_pos_flipY"]
        desktop = hou.ui.curDesktop()
        pane = desktop.createFloatingPanel(hou.paneTabType.PythonPanel, position=cursor_pos, size=(500, 200))
        pane.setName("Houdini Master")
        # qtParentWindow is a new api since 19.5 or 20.0
        if hasattr(pane, 'qtParentWindow'):
            pane.qtParentWindow().setWindowFlags(QtCore.Qt.FramelessWindowHint)
        pane_tab = pane.paneTabs()[0]
        pane_tab.showToolbar(False)
        pane_tab.setActiveInterface(hou.pypanel.interfaces()["dolag::houdini_master_AI_console"])

tmp_console_item = ConsoleItem(item_name="Ask Houdini Master", alias="chat", callback=chatgpt_cb)
CUSTOM_ITEMS.append(tmp_console_item)


# viewer wanderer
from utils import viewer_states
def viewer_wanderer_cb(context):
    viewer_states.enableSOPState("dolag::viewer_wanderer")

tmp_console_item = ConsoleItem(item_name="Viewer Wanderer WSAD", alias="walk", callback=viewer_wanderer_cb)
CUSTOM_ITEMS.append(tmp_console_item)


def merge_selected_cb(context):
    if len(context["selected_nodes"]) > 0:
        network = context["network_node"]
        merge_node = network.createNode("merge")
        index = 0
        for node in context["selected_nodes"]:
            for i in range(len(node.outputNames())):
                merge_node.setInput(index, node, i)
                index += 1

        merge_node.setPosition(context["editor_pos"])


tmp_console_item = ConsoleItem(item_name="Merge Selected", alias="merge", callback=merge_selected_cb)
CUSTOM_ITEMS.append(tmp_console_item)


def switch_selected_cb(context):
    if len(context["selected_nodes"]) > 0:
        network = context["network_node"]
        switch_node = network.createNode("switch")
        index = 0
        for node in context["selected_nodes"]:
            for i in range(len(node.outputNames())):
                switch_node.setInput(index, node, i)
                index += 1

        switch_node.setPosition(context["editor_pos"])


tmp_console_item = ConsoleItem(item_name="Switch Selected", alias="switch", callback=switch_selected_cb)
CUSTOM_ITEMS.append(tmp_console_item)

def snap_to_grid_cb(context):
    nodes = context["selected_nodes"]
    if len(nodes) == 0:
        snapToGridAllNodes()
    else:
        snapToGrid(nodes)

tmp_console_item = ConsoleItem(item_name="Nodes Snap to Grid", alias="snap", callback=snap_to_grid_cb)
CUSTOM_ITEMS.append(tmp_console_item)


def open_dependency_viewer_cb(context):
    nodes = context["selected_nodes"]
    from op_menu import node_dependency_viewer
    if len(nodes) > 0:
        node_dependency_viewer.open_dependency_viewer(nodes[0])

tmp_console_item = ConsoleItem(item_name="Open Dependency Viewer", alias="dep", callback=open_dependency_viewer_cb)
CUSTOM_ITEMS.append(tmp_console_item)


def open_unlocked_nodes_viewer_cb(context):
    from op_menu.unlocked_nodes_viewer import open_unlocked_nodes_viewer
    open_unlocked_nodes_viewer()

tmp_console_item = ConsoleItem(item_name="Open Unlocked Nodes Viewer", alias="unlock", callback=open_unlocked_nodes_viewer_cb)
CUSTOM_ITEMS.append(tmp_console_item)



