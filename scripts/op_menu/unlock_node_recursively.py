import hou
from Dolag import node as dn

def unlockNodeRecursively(node):
    node = dn.getNode(node)
    if node is None:
        return

    dn.unlockCustomNode(node)