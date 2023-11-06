import hou


def getDowmstreamNodes(node):
    # if is neither dot nor node, return empty list
    if not isinstance(node, hou.NetworkDot) and not isinstance(node, hou.Node) and not isinstance(node, hou.SubnetIndirectInput):
        return []
    
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


def getDowmstreamItems(node):
    # if is neither dot nor node, return empty list
    if not isinstance(node, hou.NetworkDot) and not isinstance(node, hou.Node) and not isinstance(node, hou.SubnetIndirectInput):
        return []

    outputs = node.outputConnections()
    outputs = [i.outputItem() for i in outputs]
    downstream_nodes = []
    for item in outputs:
        # if in downstream, discard
        if item in downstream_nodes:
            continue

        # if is just a dot, continue trace
        if isinstance(item, hou.NetworkDot):
            downstream_nodes.append(item)
            downstream_nodes.extend(getDowmstreamNodes(item))

        elif isinstance(item, hou.Node):
            downstream_nodes.append(item)

    # remove duplicates
    downstream_nodes = list(set(downstream_nodes))
    return downstream_nodes


# pure connection means that, there are only NetworkDot or Wire between two nodes
def checkPureConnection(parent, child):
    # direct link
    if parent == child:
        return True

    # if child is a Node, you are dirty
    if isinstance(child, hou.Node):
        return False

    return child in getDowmstreamItems(parent)


def wireHubInternal(top_node, original_top_node, downstream_nodes, max_vertical_height=5, dot_above_node_height=1):
    top_pos = top_node.position()
    if len(downstream_nodes) > 0:
        dot_valid = True
        second_top_node = sorted(downstream_nodes, key=lambda x: x.position()[1], reverse=True)[0]
        dot_pos = [second_top_node.position()[0] + 0.5 * second_top_node.size()[0], second_top_node.position()[1] \
                   + dot_above_node_height + 0.5 * second_top_node.size()[1]]
        nodes_in_reach = [n for n in downstream_nodes if
                          0 < dot_pos[1] - n.position()[1] + n.size()[1] * 0.5 < max_vertical_height]
        # fallback to second top node if no dot in reach
        nodes_in_reach = [second_top_node[0]] if len(nodes_in_reach) == 0 else nodes_in_reach
        nodes_out_of_reach = [n for n in downstream_nodes if n not in nodes_in_reach]

        # if dot is close to top node, discard
        if top_pos[1] - dot_pos[1] > top_node.size()[1] * 0.5 + dot_above_node_height * 1.1:
            dot = top_node.parent().createNetworkDot()
            dot.setPosition(dot_pos)
            dot.setInput(0, top_node)

            if len(nodes_in_reach) == 0:
                dot.destroy()
                dot_valid = False

            elif dot_valid:
                mean_pos_x = 0
                valid_node_count = 0
                for node in nodes_in_reach:
                    # get original
                    top_node_indices = []  # maybe exist more than one connection toward top node
                    in_connections = node.inputConnections()
                    for c in in_connections:
                        if checkPureConnection(original_top_node, c.inputItem()):
                            top_node_indices.append(c.inputIndex())

                    for index in top_node_indices:
                        node.setInput(index, dot)

                    if len(top_node_indices) > 0:
                        mean_pos_x += node.position()[0] + 0.5 * (node.size()[0] - dot.size()[0])
                        valid_node_count += 1

                if valid_node_count > 0:
                    mean_pos_x /= valid_node_count
                    dot.setPosition([mean_pos_x, dot.position()[1]])

                elif dot_valid:
                    dot.destroy()
                    dot_valid = False

            if dot_valid and len(nodes_in_reach) == 1 and len(nodes_out_of_reach) == 0:
                dot.destroy()
                dot_valid = False

            if dot_valid and len(dot.outputConnections()) == 0 and len(nodes_out_of_reach) == 0:
                dot.destroy()
                dot_valid = False

            if isinstance(top_node, hou.NetworkDot) and len(top_node.outputConnections()) == 0 and len(
                    nodes_out_of_reach) == 0:
                top_node.destroy()
                dot_valid = False

            if len(nodes_out_of_reach) > 0:
                if dot_valid:
                    wireHubInternal(dot, original_top_node, nodes_out_of_reach, max_vertical_height,
                                    dot_above_node_height)
                # if current level dot failed to create, keep the last top node and dive in
                else:
                    wireHubInternal(top_node, original_top_node, nodes_out_of_reach, max_vertical_height,
                                    dot_above_node_height)

                return

        else:
            if len(nodes_out_of_reach) > 0:
                wireHubInternal(top_node, original_top_node, nodes_out_of_reach, max_vertical_height,
                                dot_above_node_height)

            return


def wireHub(top_node, max_vertical_height=5, dot_above_node_height=1, nodes_range=None, use_undo_group=True):
    downstream_nodes = getDowmstreamItems(top_node)
    if nodes_range is not None:
        downstream_nodes = [n for n in downstream_nodes if n in nodes_range]

    if len(downstream_nodes) > 0:
        if use_undo_group:
            with hou.undos.group("Wire Hub"):
                wireHubInternal(top_node, top_node, downstream_nodes, max_vertical_height, dot_above_node_height)
                for n in downstream_nodes:
                    if isinstance(n, hou.NetworkDot) and len(n.outputConnections()) == 0:
                        n.destroy()

        else:
            wireHubInternal(top_node, top_node, downstream_nodes, max_vertical_height, dot_above_node_height)
            for n in downstream_nodes:
                if isinstance(n, hou.NetworkDot) and len(n.outputConnections()) == 0:
                    n.destroy()


def wireHubs(top_nodes, max_vertical_height=5, dot_above_node_height=1, clear_dot_island=True):
    from collections import Iterable
    if isinstance(top_nodes, Iterable):
        with hou.undos.group("Wire Hubs"):
            top_nodes = sorted(top_nodes, key=lambda x: x.position()[1], reverse=True)
            for n in top_nodes:
                wireHub(n, max_vertical_height, dot_above_node_height, top_nodes, False)

            if clear_dot_island:
                for n in top_nodes:
                    if isinstance(n, hou.NetworkDot) and len(n.outputConnections()) == 0:
                        n.destroy()
