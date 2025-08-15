from __future__ import division
import hou


def getDowmstreamNodes(node, _visited=None):
    # recursively collect ALL downstream nodes (and dots) from given node
    if _visited is None:
        _visited = set()
    if not isinstance(node, (hou.NetworkDot, hou.Node, hou.SubnetIndirectInput)):
        return []

    try:
        node_key = node.path() if hasattr(node, 'path') else str(id(node))
    except Exception:
        node_key = str(id(node))
    if node_key in _visited:
        return []
    _visited.add(node_key)

    downstream = []
    try:
        outputs = [c.outputItem() for c in node.outputConnections()]
    except Exception:
        outputs = []

    for item in outputs:
        try:
            item_key = item.path() if hasattr(item, 'path') else str(id(item))
        except Exception:
            item_key = str(id(item))
        if item_key in _visited:
            continue
        downstream.append(item)
        # Recurse through both dots and nodes to get deep downstream
        downstream.extend(getDowmstreamNodes(item, _visited))

    # dedupe while preserving order
    seen = set()
    uniq = []
    for x in downstream:
        try:
            k = x.path() if hasattr(x, 'path') else str(id(x))
        except Exception:
            k = str(id(x))
        if k not in seen:
            seen.add(k)
            uniq.append(x)
    return uniq


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

        # if is just a dot, continue tracing
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
    """Check if there's a pure connection (only dots/wires) between parent and child"""
    # direct link
    if parent == child:
        return True

    # if child is directly connected to parent (including nodes)
    parent_outputs = [conn.outputItem() for conn in parent.outputConnections()]
    if child in parent_outputs:
        return True

    # if child is a Node and not directly connected, not pure
    if isinstance(child, hou.Node):
        return False

    # for dots, check if child is in downstream path
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
        nodes_in_reach = [second_top_node] if len(nodes_in_reach) == 0 else nodes_in_reach
        nodes_out_of_reach = [n for n in downstream_nodes if n not in nodes_in_reach]

        # if dot is close to top node, discard
        if top_pos[1] - dot_pos[1] > top_node.size()[1] * 0.5 + dot_above_node_height * 1.1:
            # Build redirection groups by propagating the ORIGINAL output index from `top_node`
            # along only NetworkDots; this strictly preserves connectivity.
            from collections import deque
            def _groups_from_source(source_item):
                groups_local = {}
                visited = set()  # (item_key, origin_out_idx)
                dq = deque()
                try:
                    for c in source_item.outputConnections():
                        dq.append((c, c.outputIndex()))
                except Exception:
                    return groups_local
                while dq:
                    conn, origin_out_idx = dq.popleft()
                    try:
                        dst = conn.outputItem()
                    except Exception:
                        continue
                    key_item = None
                    try:
                        key_item = dst.path() if hasattr(dst, 'path') else str(id(dst))
                    except Exception:
                        key_item = str(id(dst))
                    if isinstance(dst, hou.NetworkDot):
                        vk = (key_item, origin_out_idx)
                        if vk in visited:
                            continue
                        visited.add(vk)
                        try:
                            for c2 in dst.outputConnections():
                                dq.append((c2, origin_out_idx))
                        except Exception:
                            pass
                    else:
                        # terminal real node: record its input index from this connection
                        try:
                            inp_idx = conn.inputIndex()
                        except Exception:
                            inp_idx = 0
                        groups_local.setdefault(origin_out_idx, []).append((dst, inp_idx))
                return groups_local

            all_groups = _groups_from_source(top_node)
            # filter groups to nodes_in_reach only
            layout_nodes = {}
            groups = {}
            reach_set = set(nodes_in_reach)
            for out_idx, pairs in all_groups.items():
                filtered = [(n, iidx) for (n, iidx) in pairs if n in reach_set]
                if not filtered:
                    continue
                groups[out_idx] = filtered
                for n, _ in filtered:
                    layout_nodes.setdefault(out_idx, set()).add(n)

            created = []
            for out_idx, targets in groups.items():
                d = top_node.parent().createNetworkDot()
                created.append(d)
                d.setPosition(dot_pos)
                try:
                    # If top_node is a real node, preserve the specific output pin
                    if isinstance(top_node, hou.Node) and not isinstance(top_node, hou.NetworkDot):
                        d.setInput(0, top_node, out_idx)
                    else:
                        d.setInput(0, top_node)
                except Exception:
                    d.setInput(0, top_node)

                for n, input_index in targets:
                    try:
                        n.setInput(input_index, d)
                    except Exception:
                        pass

                # simple x-layout for each group
                ns = list(layout_nodes.get(out_idx, []))
                if ns:
                    mean_x = sum(n.position()[0] + 0.5 * (n.size()[0] - d.size()[0]) for n in ns) / float(len(ns))
                    d.setPosition([mean_x, d.position()[1]])

            if not groups:
                dot_valid = False

            if dot_valid and len(nodes_in_reach) == 1 and len(nodes_out_of_reach) == 0:
                for d in created:
                    try:
                        d.destroy()
                    except Exception:
                        pass
                dot_valid = False

            if dot_valid and all(len(d.outputConnections()) == 0 for d in created) and len(nodes_out_of_reach) == 0:
                for d in created:
                    try:
                        d.destroy()
                    except Exception:
                        pass
                dot_valid = False

            if isinstance(top_node, hou.NetworkDot) and len(top_node.outputConnections()) == 0 and len(
                    nodes_out_of_reach) == 0:
                top_node.destroy()
                dot_valid = False

            if len(nodes_out_of_reach) > 0:
                if dot_valid:
                    next_top = created[-1] if created else top_node
                    wireHubInternal(next_top, original_top_node, nodes_out_of_reach, max_vertical_height,
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
