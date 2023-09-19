import hou
from collections.abc import Iterable
SPACE_DISTANCE = 1.5

def verticalSpacingAllNodes():
    editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    nodes = editor.currentNode().parent().allItems()
    nodes = [n for n in nodes if isinstance(n, hou.Node) or isinstance(n, hou.NetworkDot) or isinstance(n, hou.SubnetIndirectInput)]
    verticalSpacing(nodes)

def verticalSpacing(nodes):
    # get terminate nodes, terminate node is a node has no input node
    terminate_nodes = []
    end_nodes = []
    block_begin_nodes_info = []
    for node in nodes:
        # record block begin relative pos
        if isinstance(node, hou.Node) and node.type().name() == "block_begin":
            block_end_path = node.parm("blockpath").eval()
            block_end_node = node.node(block_end_path)
            if block_end_node is not None:
                pos_diff = block_end_node.position().y() - node.position().y()
                block_begin_nodes_info.append({"node": node, "block_end": block_end_node, "pos_diff": pos_diff})

        # get terminate nodes and end nodes
        if isinstance(node, hou.Node) or isinstance(node, hou.NetworkDot) or isinstance(node, hou.SubnetIndirectInput):
            inputs = node.inputConnections()
            if len(inputs) == 0:
                if node not in terminate_nodes:
                    terminate_nodes.append(node)

            # else if this node has no parent in the selected items
            else:
                is_terminate = True
                for c in inputs:
                    if c.inputItem() in nodes:
                        is_terminate = False
                        break

                if is_terminate:
                    terminate_nodes.append(node)

            outputs = node.outputConnections()
            if len(outputs) == 0:
                if node not in end_nodes:
                    end_nodes.append(node)

            # else if this node has no child in the selected items
            else:
                is_end = True
                for c in outputs:
                    if c.outputItem() in nodes:
                        is_end = False
                        break

                if is_end:
                    end_nodes.append(node)

    if len(terminate_nodes) == 0:
        return

    with hou.undos.group("Vertical Spacing Nodes"):
        nodes = {n: {"py": n.position().y(), "calc": True if n in terminate_nodes else False} for n in nodes}
        node_stack = end_nodes
        while node_stack.__len__() > 0:
            n = node_stack[-1]
            # print("node stack : " + str([nn.name() for nn in node_stack]))

            if nodes[n]["calc"] is True:
                node_stack.pop()
                continue

            # print("current node : " + n.name())

            # calc parent nodes
            parent_nodes = [c.inputItem() for c in n.inputConnections() if c.inputItem() in nodes]
            can_calc = True
            lowest_parent_pos = 100000
            not_calc_parent = []
            for parent_node in parent_nodes:
                # if parent is not calculated
                if nodes[parent_node]["calc"] is False:
                    can_calc = False
                    # push into not_calc_parent
                    if parent_node not in not_calc_parent:
                        not_calc_parent.append(parent_node)

                # else update to the lowest parent
                lowest_parent_pos = min(lowest_parent_pos, nodes[parent_node]["py"])

            # if can calculate position at this moment, set, mark and pop
            if can_calc:
                # print("calc : " + n.name())
                if nodes[n]["py"] > lowest_parent_pos:
                    nodes[n]["py"] = lowest_parent_pos - SPACE_DISTANCE

                nodes[n]["calc"] = True
                node_stack.pop()

            # else, travel parents
            else:
                node_stack.extend(not_calc_parent)

        for n in nodes.keys():
            # if is terminate node, move to top of child nodes
            if n in terminate_nodes:
                child_nodes = [c.outputItem() for c in n.outputConnections() if c.outputItem() in nodes]
                if len(child_nodes) > 0:
                    highest_child_pos = -100000
                    for child_node in child_nodes:
                        if nodes[child_node]["py"] > highest_child_pos:
                            highest_child_pos = nodes[child_node]["py"]

                nodes[n]["py"] = highest_child_pos + SPACE_DISTANCE

            n.setPosition(hou.Vector2(n.position().x(), nodes[n]["py"]))

        # recalc block begin pos
        for block_begin in block_begin_nodes_info:
            if block_begin["node"] in terminate_nodes:
                block_begin["node"].setPosition(hou.Vector2(block_begin["node"].position().x(), nodes[block_begin["block_end"]]["py"] - block_begin["pos_diff"]))

