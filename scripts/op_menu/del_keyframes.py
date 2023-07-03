"""
    Delete all keyframes including expressions of a node
"""
import hou
from Dolag import node as dn


def delKeyframes(node):
    node = dn.getNode(node)
    if node is None:
        return

    parms = node.parms()
    for parm in parms:
        parm.deleteAllKeyframes()
