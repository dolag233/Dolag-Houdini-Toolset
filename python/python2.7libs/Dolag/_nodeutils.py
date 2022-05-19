import hou


# get node from str or hou.Node
def getNode(node_desc):
    node = None
    # if input node path
    if isinstance(node_desc, str):
        node = hou.node(node_desc)

    # if input is a node instance
    elif isinstance(node, hou.Node):
        node = node_desc

    else:
        pass

    return node
