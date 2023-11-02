from canvaseventtypes import *
from nodegraphbase import EventHandler
import hou



# event handler class will not be destroyed because of coroutine
# until handleEvent return None
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
        self.src_item_type = "none"
        self.__undos_group = None

    # use dot as a marker
    def __createMarkDot(self, uievent):
        if self.mark_dot is not None and isinstance(self.mark_dot, hou.NetworkDot):
            self.mark_dot.destroy()

        else:
            self.mark_dot = uievent.editor.pwd().createNetworkDot()
            self.mark_dot.setColor(self.__marker_color)
            # set connections
            if self.src_item_type == "input":
                input_connection = None
                for ic in self.src_item.inputConnections():
                    if ic.inputIndex() == self.src_connector_index:
                        input_connection = ic
                        break

                if input_connection is not None:
                    # input has at most one connection
                    self.mark_dot.setInput(0, input_connection.inputItem())

            elif self.src_item_type == "output":
                # get output connections from this exporter
                output_connections = []
                for oc in self.src_item.outputConnections():
                    if oc.outputIndex() == self.src_connector_index:
                        output_connections.append(oc)

                for oc in output_connections:
                    output_item = oc.outputItem()
                    output_item.setInput(oc.inputIndex(), self.mark_dot)

            elif self.src_item_type == "dot":
                for ic in self.src_item.inputConnections():
                    self.mark_dot.setInput(ic.inputIndex(), ic.inputItem())

                for oc in self.src_item.outputConnections():
                    output_item = oc.outputItem()
                    output_item.setInput(oc.inputIndex(), self.mark_dot)

        self.__moveMarkDot(uievent)


    # return connector item and type string
    def __getNearConnector(self, uievent, distance_threshold):
        cursor_pos = self.__getEditorPos(uievent)
        editor = uievent.editor
        # in_range_items, _, _ = editor.networkItemsInBox(cursor_pos - hou.Vector2(2, 2), cursor_pos + hou.Vector2(2, 2))
        in_range_items = editor.pwd().allItems()
        in_range_items = [item for item in in_range_items if cursor_pos.distanceTo(item.position()) < 2]
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

        return src_item, src_item_type, src_connector_index, src_connector_pos

    def __updateNearConnector(self, uievent):
        src_item, src_type, src_connector_index, _ = self.__getNearConnector(uievent, self.__detect_radius)
        self.src_item = src_item
        self.src_item_type = src_type
        self.src_connector_index = src_connector_index

    def __moveMarkDot(self, uievent):
        cursor_pos = self.__getEditorPos(uievent)
        # try to snap
        if self.mark_dot is not None:
            connector_item, __, ___, connector_pos = self.__getNearConnector(uievent, self.__detect_radius)
            if connector_item is not None:
                self.mark_dot.setPosition(connector_pos)
            else:
                self.mark_dot.setPosition(cursor_pos)


    def __drop(self, uievent):
        success = False
        if self.src_item is not None and self.mark_dot is not None:
            dst_item, dst_type, dst_connector_index, _ = self.__getNearConnector(uievent, self.__detect_radius)
            if self.src_item_type == 'input' and dst_type == 'input':
                # if is input, just set because input connection is unique
                dst_item.setInput(dst_connector_index, self.mark_dot.inputConnections()[0].inputItem(), self.mark_dot.inputConnections()[0].inputIndex())
                # delete original connection
                self.src_item.setInput(self.src_connector_index, None)
                success = True

            elif self.src_item_type == 'output' and dst_type == 'output':
                for oc in self.mark_dot.outputConnections():
                    oc.inputItem().setInput(oc.inputIndex(), dst_item, dst_connector_index)
                    success = True

            elif self.src_item_type == 'dot':
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

        if not success:
            if self.src_item_type == "output":
                for oc in self.mark_dot.outputConnections():
                    oc.outputItem().setInput(oc.inputIndex(), self.src_item, self.src_connector_index)

        self.mark_dot.destroy()

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
                    uievent.modifierstate.alt and uievent.modifierstate.ctrl:

                self.__moveMarkDot(uievent)
                # @TODO snap to other connector
                return self

            # else, end dragging
            else:
                self.__drop(uievent)
                self.__end_undos_group()
                self.__cleanState()
                return None
