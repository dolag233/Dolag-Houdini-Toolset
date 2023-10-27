import hou


def getDowmstreamNodes(node):
    outputs = node.outputConnections()
    outputs = [i.outputItem() for i in outputs]
    downstream_nodes = []
    for item in outputs:
        # if in downstream, discard
        if item in downstream_nodes:
            continue

        # if is just a dot, continue trace
        if isinstance(item, hou.NetworkDot):
            downstream_nodes.extend(getDowmstreamNodes(item))

        elif isinstance(item, hou.Node):
            downstream_nodes.append(item)

    # remove duplicates
    downstream_nodes = list(set(downstream_nodes))
    return downstream_nodes

# pure connection means that, there are only NetworkDot or Wire between two nodes
def checkPureConnection(node0, node1):
    return (node1 in getDowmstreamNodes(node0)) or (node0 in getDowmstreamNodes(node1))

def wireHubInternal(top_node, original_top_node, downstream_nodes, max_vertical_height = 5, dot_above_node_height = 0.5):
    top_pos = top_node.position()
    nodes_in_reach = [n for n in downstream_nodes if top_pos[1] - n.position()[1] <= max_vertical_height]
    nodes_out_of_reach = [n for n in downstream_nodes if 0 > top_pos[1] - n.position()[1] > max_vertical_height]
    dot = top_node.parent().createNetworkDot()
    second_top_node = sorted(nodes_in_reach, key=lambda x: x.position()[1])[0]
    dot.setPosition([second_top_node.position()[0], second_top_node.position()[1] + dot_above_node_height])
    for node in nodes_in_reach:
        # get original
        top_node_index = 0
        top_node_indices = []  # maybe exist more than one connection toward top node
        in_connections = node.inputConnections()
        for c in range(len(in_connections)):
            if checkPureConnection(original_top_node, in_connections[c].inputItem()):
                top_node_indices.append(top_node_index)
                break

            top_node_index += 1

        for index in top_node_indices:
            node.setInput(index, dot)

    if len(nodes_out_of_reach) > 0:
        wireHubInternal(dot, original_top_node, nodes_out_of_reach, max_vertical_height, dot_above_node_height)

def wireHub(top_node, max_vertical_height = 5, dot_above_node_height = 0.5):
    top_pos = top_node.position()
    downstream_nodes = getDowmstreamNodes(top_node)
    wireHubInternal(top_node, top_node, downstream_nodes, max_vertical_height, dot_above_node_height)