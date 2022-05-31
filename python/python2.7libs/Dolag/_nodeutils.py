import hou


# get node from str or hou.Node
def getNode(node_desc, node_type=hou.Node):
    node = None
    # if input node path
    if isinstance(node_desc, str):
        node = hou.node(node_desc)

    # if node_type is not tuple
    elif (not isinstance(node_type, tuple)) and isinstance(node_desc, node_type):
        node = node_desc

    elif isinstance(node_type, tuple):
        for nt in node_type:
            if isinstance(node_desc, nt):
                node = node_desc

    else:
        pass

    return node
