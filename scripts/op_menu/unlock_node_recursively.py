import hou
from Dolag import node as dn
from collections.abc import Iterable

def unlockNodeRecursively(node):
    node = dn.getNode(node)
    if node is None:
        return

    dn.unlockCustomNode(node)
    