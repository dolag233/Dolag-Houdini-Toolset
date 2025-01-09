from canvaseventtypes import *
from nodegraphbase import EventHandler
import hou


# exchange input, outputs, dot's connections to another node
# press Ctrl + Alt and drag connector
class ExchangerHandler(EventHandler):
    def __init__(self, uievent):
        super(ExchangerHandler, self).__init__(uievent)
        self.__cleanState()
        self.__marker_color = hou.Color(1.0, 0.2, 0.1)
        self.__detect_radius = 0.5

    def __cleanState(self):
        self.mark_dot = None
        self.is_moving = False
        self.src_item = None
        self.src_connector_index = 0
        self.src_merge_input_indices = []
        self.src_type = "none"
        self.src_is_merge = False
        self.src_is_subnet_input = False
        self.__undos_group = None

    def __checkMerge(self, node):
        if not isinstance(node, hou.Node):
            return False

        merge_type = ['merge', 'switch', 'vdbmerge']
        merge_inputs_threshold = 28
        node_type = node.type()
        if node_type.name() in merge_type or node_type.maxNumInputs() >= merge_inputs_threshold:
            return True

        return False

    def __destroyMarkDot(self):
        if self.mark_dot is not None:
            if isinstance(self.mark_dot, hou.NetworkDot):
                self.mark_dot.destroy()

            elif isinstance(self.mark_dot, list):
                for dot in self.mark_dot:
                    if isinstance(dot, hou.NetworkDot):
                        dot.destroy()

            self.mark_dot = None

    # use dot as a marker
    def __createMarkDot(self, uievent):
        self.__destroyMarkDot()

        if self.src_is_merge and self.src_type == "input":
            # create some dots
            self.mark_dot = []
            for ic in self.src_item.inputConnections():
                tmp_mark_dot = uievent.editor.pwd().createNetworkDot()
                tmp_mark_dot.setColor(self.__marker_color)
                self.mark_dot.append(tmp_mark_dot)

        else:
            # create single dot
            self.mark_dot = uievent.editor.pwd().createNetworkDot()
            self.mark_dot.setColor(self.__marker_color)

        # set connections
        if self.src_type == "input":
            # if src is merge node, create tons of dots
            if self.src_is_merge and isinstance(self.mark_dot, list):
                i = 0
                for ic in self.src_item.inputConnections():
                    self.mark_dot[i].setInput(0, ic.inputItem(), ic.outputIndex())
                    i += 1
                    # delete original input connection
                    # remove index 0 because when you delete one input, the rest indices will be moved automatically
                    self.src_item.setInput(0, None)

            else:
                input_connection = None
                for ic in self.src_item.inputConnections():
                    if ic.inputIndex() == self.src_connector_index:
                        input_connection = ic
                        break

                if input_connection is not None:
                    # input has at most one connection
                    self.mark_dot.setInput(0, input_connection.inputItem(), input_connection.outputIndex())
                    # delete original input connection
                    self.src_item.setInput(self.src_connector_index, None)

        elif self.src_type == "output":
            # get output connections from this exporter
            output_connections = []
            for oc in self.src_item.outputConnections():
                if oc.outputIndex() == self.src_connector_index:
                    output_connections.append(oc)

            for oc in output_connections:
                output_item = oc.outputItem()
                output_item.setInput(oc.inputIndex(), self.mark_dot)

        elif self.src_type == "dot":
            for ic in self.src_item.inputConnections():
                self.mark_dot.setInput(ic.inputIndex(), ic.inputItem())

            for oc in self.src_item.outputConnections():
                output_item = oc.outputItem()
                output_item.setInput(oc.inputIndex(), self.mark_dot)

        self.__moveMarkDot(uievent)

    # return connector item and type string
    def __getNearConnector(self, uievent, distance_threshold, excluded_items=None):
        cursor_pos = self.__getEditorPos(uievent)
        editor = uievent.editor
        # in_range_items, _, _ = editor.networkItemsInBox(cursor_pos - hou.Vector2(2, 2), cursor_pos + hou.Vector2(2, 2))
        in_range_items = editor.pwd().allItems()
        excluded_items = [] if excluded_items is None or not isinstance(excluded_items, list) else excluded_items
        in_range_items = [item for item in in_range_items if cursor_pos.distanceTo(item.position()) < 2 and item not in excluded_items]
        src_item = None
        src_item_type = "none"
        src_connector_index = 0
        src_connector_pos = hou.Vector2(0, 0)
        nearest_distance = 114514
        for item in in_range_items:
            if item == self.mark_dot:
                continue

            # if is a dot, check dot pos
            if isinstance(item, hou.NetworkDot):
                distance = item.position().distanceTo(cursor_pos)
                if distance < distance_threshold:
                    src_item = item
                    src_item_type = "dot"
                    src_connector_pos = item.position()

            # if is a node, check inputs and outputs
            elif isinstance(item, hou.Node):
                # check inputs
                for index in range(len(item.inputLabels())):
                    input_pos = editor.itemInputPos(item, index)
                    distance = input_pos.distanceTo(cursor_pos)
                    if distance < distance_threshold and distance < nearest_distance:
                        nearest_distance = distance
                        src_item = item
                        src_item_type = "input"
                        src_connector_index = index
                        src_connector_pos = input_pos

                # check inputs
                for index in range(len(item.outputLabels())):
                    output_pos = editor.itemOutputPos(item, index)
                    distance = output_pos.distanceTo(cursor_pos)
                    if distance < distance_threshold and distance < nearest_distance:
                        nearest_distance = distance
                        src_item = item
                        src_item_type = "output"
                        src_connector_index = index
                        src_connector_pos = output_pos

            elif isinstance(item, hou.SubnetIndirectInput):
                output_pos = editor.itemOutputPos(item, 0)
                distance = output_pos.distanceTo(cursor_pos)
                if distance < distance_threshold and distance < nearest_distance:
                    nearest_distance = distance
                    src_item = item
                    src_item_type = "output"
                    src_connector_index = 0
                    src_connector_pos = output_pos
                    self.src_is_subnet_input = True

        return src_item, src_item_type, src_connector_index, src_connector_pos

    def __updateNearConnector(self, uievent):
        src_item, src_type, src_connector_index, _ = self.__getNearConnector(uievent, self.__detect_radius)
        self.src_item = src_item
        self.src_type = src_type
        self.src_connector_index = src_connector_index
        self.src_is_merge = True if self.__checkMerge(src_item) else False

    def __moveMarkDot(self, uievent):
        cursor_pos = self.__getEditorPos(uievent)
        # try to move or snap
        if self.mark_dot is not None:
            if self.src_is_merge and isinstance(self.mark_dot, list):
                connector_item, __, ___, connector_pos = self.__getNearConnector(uievent, self.__detect_radius, excluded_items=self.mark_dot)
                if connector_item is not None:
                    for dot in self.mark_dot:
                        dot.setPosition(connector_pos)

                else:
                    if len(self.mark_dot) > 1:
                        interval = self.src_item.size()[1] / (len(self.mark_dot) - 1)
                        start_pos_x = cursor_pos[0] - interval * (len(self.mark_dot) - 1) / 2.0
                        i = 0
                        for dot in self.mark_dot:
                            dot.setPosition(hou.Vector2(start_pos_x + i * 0.1, cursor_pos[1]))
                            i += 1

                    else:
                        # this merge node has only one input
                        self.mark_dot[0].setPosition(cursor_pos)

            else:
                connector_item, __, ___, connector_pos = self.__getNearConnector(uievent, self.__detect_radius)
                if connector_item is not None:
                    self.mark_dot.setPosition(connector_pos)
                else:
                    self.mark_dot.setPosition(cursor_pos)

    def __drop(self, uievent):
        success = False
        skip = False
        dst_item, dst_type, dst_connector_index, _ = self.__getNearConnector(uievent, self.__detect_radius, self.mark_dot)
        if self.src_item is None or self.mark_dot is None or dst_item is None:
            skip = True

        if self.src_item == dst_item:
            if self.src_type == 'dot' and dst_type == 'dot':

                skip = True

            elif self.src_type == dst_type and self.src_connector_index == dst_connector_index:
                skip = True

        if not skip:
            if self.src_type == 'input' and dst_type == 'input':
                # if they are merge node
                if self.src_is_merge and isinstance(self.mark_dot, list):
                    if self.__checkMerge(dst_item):
                        i = len(dst_item.inputs())
                        for dot in self.mark_dot:
                            dst_item.setInput(i, dot.inputConnections()[0].inputItem(),
                                              dot.inputConnections()[0].outputIndex())
                            i += 1

                        success = True

                    else:
                        dst_item.setInput(0, self.mark_dot[0].inputConnections()[0].inputItem(),
                                          self.mark_dot[0].inputConnections()[0].outputIndex())
                        success = True

                else:
                    # if is input, just set because input connection is unique
                    dst_item.setInput(dst_connector_index, self.mark_dot.inputConnections()[0].inputItem(), self.mark_dot.inputConnections()[0].outputIndex())
                    # delete original connection
                    self.src_item.setInput(self.src_connector_index, None)
                    success = True

            elif self.src_type == 'output' and dst_type == 'output':
                for oc in self.mark_dot.outputConnections():
                    # if the dest node is the ancestor (or self) node of the output connection node
                    # restore the connection between the src node and this output connection node
                    if not self.src_is_subnet_input:
                        if oc.outputItem() in dst_item.inputAncestors() or oc.outputItem() == dst_item:
                            oc.outputItem().setInput(oc.inputIndex(), self.src_item, self.src_connector_index)
                        else:
                            oc.inputItem().setInput(oc.inputIndex(), dst_item, dst_connector_index)
                    else:
                        oc.inputItem().setInput(oc.inputIndex(), dst_item, dst_connector_index)
                    success = True

            elif self.src_type == 'dot':
                if dst_type == 'dot':
                    # copy input
                    if len(self.mark_dot.inputConnections()) != 0:
                        dst_item.setInput(0, self.mark_dot.inputConnections()[0].inputItem(), self.mark_dot.inputConnections()[0].inputIndex())

                    # copy outputs
                    for oc in self.mark_dot.outputConnections():
                        oc.inputItem().setInput(oc.inputIndex(), dst_item, dst_connector_index)

                    success = True

                elif dst_type == 'output':
                    # copy outputs
                    for oc in self.mark_dot.outputConnections():
                        oc.inputItem().setInput(oc.inputIndex(), dst_item, dst_connector_index)

                    success = True

                elif dst_type == 'input':
                    # copy input
                    if len(self.mark_dot.inputConnections()) != 0:
                        dst_item.setInput(0, self.mark_dot.inputConnections()[0].inputItem(), self.mark_dot.inputConnections()[0].inputIndex())

                    success = True

                if success:
                    # delete original dot
                    self.src_item.destroy()

        # restore original connections
        if not success:
            # restore original connections
            if self.src_item is not None and self.mark_dot is not None:
                if self.src_type == "output":
                    for oc in self.mark_dot.outputConnections():
                        oc.outputItem().setInput(oc.inputIndex(), self.src_item, self.src_connector_index)

                elif self.src_type == "input":
                    if self.src_is_merge and isinstance(self.mark_dot, list):
                        i = 0
                        for dot in self.mark_dot:
                            self.src_item.setInput(i, dot.inputConnections()[0].inputItem(), dot.inputConnections()[0].outputIndex())
                            i += 1
                    else:
                        self.src_item.setInput(self.src_connector_index, self.mark_dot.inputConnections()[0].inputItem(), self.mark_dot.inputConnections()[0].inputIndex())

        self.__destroyMarkDot()

    def __getEditorPos(self, uievent):
        return uievent.editor.posFromScreen(uievent.mousepos)

    def __begin_undos_group(self):
        if self.__undos_group is not None:
            del self.__undos_group

        else:
            self.__undos_group = hou.undos.group("Exchange Connections")
            self.__undos_group.__enter__()

    def __end_undos_group(self):
        if self.__undos_group is not None:
            del self.__undos_group
            self.__undos_group = None

    def handleEvent(self, uievent, pending_actions):
        # if cursor near to node input, output or a network dot
        # this is the beginning of the event handler
        if self.src_item is None:
            self.__updateNearConnector(uievent)
            if self.src_item is None:
                self.__cleanState()
                return None
            else:
                self.__begin_undos_group()
                self.__createMarkDot(uievent)
                return self

        else:
            # if dragging
            if isinstance(uievent, MouseEvent) and \
                uievent.mousestate.lmb and\
                    uievent.modifierstate.alt and uievent.modifierstate.ctrl and not uievent.modifierstate.shift:

                self.__moveMarkDot(uievent)
                return self

            # if dropping
            else:
                self.__drop(uievent)
                self.__end_undos_group()
                self.__cleanState()
                return None
