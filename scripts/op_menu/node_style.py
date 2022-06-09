"""
    copy and paste node shape, color
"""
import hou
from Dolag import node as dn
from Dolag import utils as du


def getNodeShape(node):
    node = dn.getNode(node)
    if node is None:
        return

    shape = node.userData("nodeshape")
    # if node shape is default
    if shape is None:
        item = node.item('.')
        shape = item.type().defaultShape()

    # default shape of rect node is ''
    if shape == '':
        shape = 'rect'

    return shape


def copyNodeShape(node):
    shape = getNodeShape(node)
    if shape is None:
        return

    hou.ui.copyTextToClipboard(shape)


def pasteNodeShape(node):
    node = dn.getNode(node)
    if node is None:
        return

    shape = hou.ui.getTextFromClipboard()
    editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    if shape != '' and shape not in editor.nodeShapes():
        return

    node.setUserData("nodeshape", shape)


def getNodeColor(node):
    node = dn.getNode(node)
    if node is None:
        return

    color = node.color()
    # color = "0.354;0.114;0.514"
    color = ';'.join(map(str, color.rgb()))
    return color


def copyNodeColor(node):
    color = getNodeColor(node)
    if color is None:
        return

    hou.ui.copyTextToClipboard(color)


def pasteNodeColor(node):
    node = dn.getNode(node)
    if node is None:
        return

    color = hou.ui.getTextFromClipboard()
    try:
        color = map(float, color.split(';'))
        node.setColor(hou.Color(*color))
    except:
        return


def copyNodeStyle(node):
    shape = getNodeShape(node)
    color = getNodeColor(node)
    if shape is None or color is None:
        return

    style = "{0}-{1}".format(shape, color)
    hou.ui.copyTextToClipboard(style)


def pasteNodeStyle(node):
    style = hou.ui.getTextFromClipboard()
    try:
        shape, color = style.split('-')
        editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if shape != '' and shape not in editor.nodeShapes():
            return

        node.setUserData("nodeshape", shape)
        color = map(float, color.split(';'))
        node.setColor(hou.Color(*color))

    except:
        return
