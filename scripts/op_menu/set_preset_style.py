"""
    set preset style
"""
import hou
# import json
from Dolag import node as dn
from Dolag import utils as du

preset_style_dict = {"input" : ((0.95, 0.8, 0.35), "diamond"), "output" : ((0.35, 0.8, 0.95), "diamond"),
                    "global control" : ((0.32, 0.258, 0.578), "cloud"), "heavy" :  (0.85, 0.075, 0.075, "")}

def setNodeColor(node, color):
    if node is None or len(color) != 3:
        return

    try:
        node.setColor(hou.Color(*color))
    except:
        return


def setNodeShape(node, shape):
    if node is None:
        return

    editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    if shape != '' and shape not in editor.nodeShapes():
        return

    node.setUserData("nodeshape", shape)


def setNodeStyle(node, color, shape):
    setNodeColor(node, color)
    setNodeShape(node, shape)


def setNodePresetStyle(node, style_name):
    if style_name not in preset_style_dict:
        return

    style = preset_style_dict[style_name]
    setNodeStyle(node, style[0], style[1])

