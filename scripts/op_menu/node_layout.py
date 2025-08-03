import hou
import math
SPACE_DISTANCE = 1.5
MIN_VERTICAL_SPACE = 1.25
MIN_COMPRESSION_DISTANCE = 5
HORIZONTAL_SPACE = 2
GRID_SIZE_X = 2  # Horizontal grid spacing
GRID_SIZE_Y = 1  # Vertical grid spacing

def verticalSpacingAllNodes(upward = False):
    editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    nodes = editor.currentNode().parent().allItems()
    verticalSpacing(nodes, upward)

def verticalCompressingAllNodes(upward=False):
    editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    nodes = editor.currentNode().parent().allItems()
    verticalCompressing(nodes, upward)

def snapToGrid(nodes, use_floor=False):
    """Snap nodes to grid alignment with different horizontal and vertical spacing
    
    Args:
        nodes: List of nodes to snap
        use_floor: If True, use floor alignment; if False, use round alignment
    """
    with hou.undos.group("Snap to Grid"):
        for node in nodes:
            if isinstance(node, hou.Node) or isinstance(node, hou.NetworkDot):
                pos = node.position()
                if use_floor:
                    new_x = math.floor(pos.x() / GRID_SIZE_X) * GRID_SIZE_X
                    new_y = math.floor(pos.y() / GRID_SIZE_Y) * GRID_SIZE_Y
                else:
                    new_x = round(pos.x() / GRID_SIZE_X) * GRID_SIZE_X
                    new_y = round(pos.y() / GRID_SIZE_Y) * GRID_SIZE_Y
                node.setPosition(hou.Vector2(new_x, new_y))

def snapToGridAllNodes():
    """Snap all nodes in current network to grid"""
    editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    nodes = editor.currentNode().parent().allItems()
    snapToGrid(nodes)

def distributeHorizontally(nodes_at_same_level, center_x=None):
    """Distribute nodes horizontally while keeping same Y position - only if necessary"""
    if len(nodes_at_same_level) <= 1:
        return
    
    # Sort nodes by current X position
    sorted_nodes = sorted(nodes_at_same_level, key=lambda n: n.position().x())
    
    # Check if redistribution is necessary
    needs_redistribution = False
    min_spacing = HORIZONTAL_SPACE * 0.5  # Minimum acceptable spacing
    
    # Check for overlaps or insufficient spacing
    for i in range(len(sorted_nodes) - 1):
        current_node = sorted_nodes[i]
        next_node = sorted_nodes[i + 1]
        
        current_right = current_node.position().x() + current_node.size().x() / 2
        next_left = next_node.position().x() - next_node.size().x() / 2
        actual_spacing = next_left - current_right
        
        # If nodes are too close or overlapping
        if actual_spacing < min_spacing:
            needs_redistribution = True
            break
    
    # Check if nodes are excessively spread out (more than 3x normal spacing)
    if not needs_redistribution and len(sorted_nodes) > 1:
        max_spacing = HORIZONTAL_SPACE * 3
        for i in range(len(sorted_nodes) - 1):
            current_node = sorted_nodes[i]
            next_node = sorted_nodes[i + 1]
            
            current_right = current_node.position().x() + current_node.size().x() / 2
            next_left = next_node.position().x() - next_node.size().x() / 2
            actual_spacing = next_left - current_right
            
            if actual_spacing > max_spacing:
                needs_redistribution = True
                break
    
    # Only redistribute if necessary
    if not needs_redistribution:
        return
    
    # Calculate total width needed for redistribution
    total_node_width = sum(node.size().x() for node in sorted_nodes)
    total_spacing = (len(sorted_nodes) - 1) * HORIZONTAL_SPACE
    total_width = total_node_width + total_spacing
    
    # Determine starting position
    if center_x is not None:
        start_x = center_x - total_width / 2
    else:
        # Use current center of existing nodes as reference
        current_left = sorted_nodes[0].position().x() - sorted_nodes[0].size().x() / 2
        current_right = sorted_nodes[-1].position().x() + sorted_nodes[-1].size().x() / 2
        current_center = (current_left + current_right) / 2
        start_x = current_center - total_width / 2
    
    # Position nodes
    current_x = start_x
    for node in sorted_nodes:
        node_size = node.size()
        new_pos = hou.Vector2(current_x + node_size.x() / 2, node.position().y())
        node.setPosition(new_pos)
        current_x += node_size.x() + HORIZONTAL_SPACE

def groupNodesByLevel(nodes):
    """Group nodes that are at the same level (connect to same outputs)"""
    level_groups = {}
    
    for node in nodes:
        if not (isinstance(node, hou.Node) or isinstance(node, hou.NetworkDot)):
            continue
            
        # Create a key based on output connections
        output_key = tuple(sorted([conn.outputItem().name() for conn in node.outputConnections() 
                                 if conn.outputItem() in nodes]))
        
        if not output_key:  # No outputs, group by Y position
            y_pos = round(node.position().y() * 2) / 2  # Round to 0.5 increments
            output_key = ("end_level", y_pos)
        
        if output_key not in level_groups:
            level_groups[output_key] = []
        level_groups[output_key].append(node)
    
    return level_groups



def verticalSpacing(nodes, upward = False):
    network_boxes = [n for n in nodes if isinstance(n, hou.NetworkBox)]
    nodes = [n for n in nodes if isinstance(n, hou.Node) or isinstance(n, hou.NetworkDot) or isinstance(n, hou.SubnetIndirectInput)]
    # get terminate nodes, terminate node is a node has no input node
    terminate_nodes = []
    end_nodes = []
    block_begin_nodes_info = []
    for node in nodes:
        # record block begin relative pos
        if isinstance(node, hou.Node) and node.type().name() == "block_begin":
            block_end_path = node.parm("blockpath").eval()
            block_end_node = node.node(block_end_path)
            if block_end_node is not None and block_end_node in nodes:
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
        if not upward:
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
                    if nodes[n]["py"] > lowest_parent_pos - MIN_VERTICAL_SPACE * n.size().y():
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
                            if nodes[child_node]["py"] > highest_child_pos + MIN_VERTICAL_SPACE * child_node.size().y():
                                highest_child_pos = nodes[child_node]["py"]

                        nodes[n]["py"] = highest_child_pos + SPACE_DISTANCE

                n.setPosition(hou.Vector2(n.position().x(), nodes[n]["py"]))

            # horizontal distribution for nodes at same level (downward flow)
            node_list = [n for n in nodes.keys() if isinstance(n, hou.Node) or isinstance(n, hou.NetworkDot)]
            level_groups = groupNodesByLevel(node_list)
            
            for group_key, group_nodes in level_groups.items():
                if len(group_nodes) > 1:
                    # Calculate center X position based on their outputs
                    center_x = None
                    if not group_key[0].startswith("end_level"):
                        # Find common output nodes
                        output_nodes = []
                        for node in group_nodes:
                            outputs = [conn.outputItem() for conn in node.outputConnections() 
                                     if conn.outputItem() in node_list]
                            output_nodes.extend(outputs)
                        
                        if output_nodes:
                            center_x = sum(out.position().x() for out in output_nodes) / len(output_nodes)
                    
                    distributeHorizontally(group_nodes, center_x)

        else:
            nodes = {n: {"py": n.position().y(), "calc": True if n in end_nodes else False} for n in nodes}
            node_stack = terminate_nodes
            while node_stack.__len__() > 0:
                n = node_stack[-1]
                # print("node stack : " + str([nn.name() for nn in node_stack]))

                if nodes[n]["calc"] is True:
                    node_stack.pop()
                    continue

                # print("current node : " + n.name())

                # calc child nodes
                child_nodes = [c.outputItem() for c in n.outputConnections() if c.outputItem() in nodes]
                can_calc = True
                highest_child_pos = -100000
                not_calc_child = []
                for child_node in child_nodes:
                    # if child is not calculated
                    if nodes[child_node]["calc"] is False:
                        can_calc = False
                        # push into not_calc_child
                        if child_node not in not_calc_child:
                            not_calc_child.append(child_node)

                    # else update to the lowest parent
                    highest_child_pos = max(highest_child_pos, nodes[child_node]["py"])

                # if can calculate position at this moment, set, mark and pop
                if can_calc:
                    # print("calc : " + n.name())
                    if nodes[n]["py"] < highest_child_pos + MIN_VERTICAL_SPACE * n.size().y():
                        nodes[n]["py"] = highest_child_pos + SPACE_DISTANCE

                    nodes[n]["calc"] = True
                    node_stack.pop()

                # else, travel parents
                else:
                    node_stack.extend(not_calc_child)

            for n in nodes.keys():
                # if is terminate node, move to top of child nodes
                if n in end_nodes:
                    parent_nodes = [c.inputItem() for c in n.inputConnections() if c.inputItem() in nodes]
                    if len(parent_nodes) > 0:
                        lowest_child_pos = 100000
                        for parent_node in parent_nodes:
                            if nodes[parent_node]["py"] < lowest_child_pos - MIN_VERTICAL_SPACE * parent_node.size().y():
                                lowest_child_pos = nodes[parent_node]["py"]

                        nodes[n]["py"] = lowest_child_pos - SPACE_DISTANCE

                n.setPosition(hou.Vector2(n.position().x(), nodes[n]["py"]))

            # horizontal distribution for nodes at same level (upward flow)
            node_list = [n for n in nodes.keys() if isinstance(n, hou.Node) or isinstance(n, hou.NetworkDot)]
            level_groups = groupNodesByLevel(node_list)
            
            for group_key, group_nodes in level_groups.items():
                if len(group_nodes) > 1:
                    # Calculate center X position based on their outputs
                    center_x = None
                    if not group_key[0].startswith("end_level"):
                        # Find common output nodes
                        output_nodes = []
                        for node in group_nodes:
                            outputs = [conn.outputItem() for conn in node.outputConnections() 
                                     if conn.outputItem() in node_list]
                            output_nodes.extend(outputs)
                        
                        if output_nodes:
                            center_x = sum(out.position().x() for out in output_nodes) / len(output_nodes)
                    
                    distributeHorizontally(group_nodes, center_x)

        # recalc block begin pos
        for block_begin in block_begin_nodes_info:
            if len(block_begin["node"].outputConnections()) == 0:
                block_begin["node"].setPosition(hou.Vector2(block_begin["node"].position().x(), nodes[block_begin["block_end"]]["py"] - block_begin["pos_diff"]))

        # auto resize network boxes
        for b in network_boxes:
            b.fitAroundContents()
        
        # snap to grid after layout (using floor alignment)
        node_list = [n for n in nodes.keys() if isinstance(n, hou.Node) or isinstance(n, hou.NetworkDot)]
        snapToGrid(node_list, use_floor=True)


def verticalCompressing(nodes, upward = False):
    network_boxes = [n for n in nodes if isinstance(n, hou.NetworkBox)]
    nodes = [n for n in nodes if isinstance(n, hou.Node) or isinstance(n, hou.NetworkDot) or isinstance(n, hou.SubnetIndirectInput)]
    # get terminate nodes, terminate node is a node has no input node
    terminate_nodes = []
    end_nodes = []
    block_begin_nodes_info = []
    for node in nodes:
        # record block begin relative pos
        if isinstance(node, hou.Node) and node.type().name() == "block_begin":
            block_end_path = node.parm("blockpath").eval()
            block_end_node = node.node(block_end_path)
            if block_end_node is not None and block_end_node in nodes:
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
        if not upward:
            nodes = {n: {"py": n.position().y(), "calc": True if n in end_nodes else False} for n in nodes}
            node_stack = terminate_nodes
            while node_stack.__len__() > 0:
                n = node_stack[-1]
                # print("node stack : " + str([nn.name() for nn in node_stack]))

                if nodes[n]["calc"] is True:
                    node_stack.pop()
                    continue

                # print("current node : " + n.name())

                # calc child nodes
                child_nodes = [c.outputItem() for c in n.outputConnections() if c.outputItem() in nodes]
                can_calc = True
                highest_child_pos = -100000
                not_calc_child = []
                for child_node in child_nodes:
                    # if child is not calculated
                    if nodes[child_node]["calc"] is False:
                        can_calc = False
                        # push into not_calc_child
                        if child_node not in not_calc_child:
                            not_calc_child.append(child_node)

                    # else update to the lowest parent
                    highest_child_pos = max(highest_child_pos, nodes[child_node]["py"])

                # if can calculate position at this moment, set, mark and pop
                if can_calc:
                    # print("calc : " + n.name())
                    if nodes[n]["py"] - highest_child_pos > MIN_COMPRESSION_DISTANCE:
                        nodes[n]["py"] = highest_child_pos + SPACE_DISTANCE

                    nodes[n]["calc"] = True
                    node_stack.pop()

                # else, travel parents
                else:
                    node_stack.extend(not_calc_child)

            for n in nodes.keys():
                n.setPosition(hou.Vector2(n.position().x(), nodes[n]["py"]))

        else:
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
                    if lowest_parent_pos - nodes[n]["py"] > MIN_COMPRESSION_DISTANCE:
                        nodes[n]["py"] = lowest_parent_pos - SPACE_DISTANCE


                    nodes[n]["calc"] = True
                    node_stack.pop()

                # else, travel parents
                else:
                    node_stack.extend(not_calc_parent)

            for n in nodes.keys():
                n.setPosition(hou.Vector2(n.position().x(), nodes[n]["py"]))

        # recalc block begin pos
        for block_begin in block_begin_nodes_info:
            if len(block_begin["node"].outputConnections()) == 0:
                block_begin["node"].setPosition(hou.Vector2(block_begin["node"].position().x(), nodes[block_begin["block_end"]]["py"] - block_begin["pos_diff"]))

        # auto resize network boxes
        for b in network_boxes:
            b.fitAroundContents()
        
        # snap to grid after layout (using floor alignment)
        node_list = [n for n in nodes.keys() if isinstance(n, hou.Node) or isinstance(n, hou.NetworkDot)]
        snapToGrid(node_list, use_floor=True)

