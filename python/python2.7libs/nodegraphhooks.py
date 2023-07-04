"""
    intercept event in Network editor
"""
import math
import time

from canvaseventtypes import *
from nodegraphconsole import KeyEventHandler

__last_mouse_state = False
__last_mouse_click_time = time.time()
__mouse_double_click_delta_time = 0.4

# Ctrl + Space to summon hot console
def createEventHandler(uievent, pending_actions):
    global __last_mouse_state
    global __last_mouse_click_time
    global __mouse_double_click_delta_time
    if isinstance(uievent, KeyboardEvent) and \
            uievent.eventtype == 'keyhit' and \
            uievent.key == 'Ctrl+Space':
        event_handler = KeyEventHandler(uievent)
        return event_handler, True if event_handler is not None else False

    elif isinstance(uievent, MouseEvent) and \
            uievent.eventtype == 'mousedown':

        import hou
        nodes = hou.selectedNodes()
        if len(nodes) == 0:
            return None, False

        cur_time = time.time()

        ## time out
        if time.time() - __last_mouse_click_time > __mouse_double_click_delta_time:
            __last_mouse_state = False
            __last_mouse_click_time = 0

        for node in nodes:
            if node.type().name() == 'Dolag_portal':
                node_pos = node.position()
                mouse_pos = uievent.editor.posFromScreen(uievent.mousepos)
                dist = node_pos.distanceTo(mouse_pos)
                if(dist > 1):
                    return None, False

                # double click
                if __last_mouse_state:
                    node.parm("teleport").pressButton()
                    __last_mouse_state = False
                    __last_mouse_click_time = 0

                # first time
                else:
                    __last_mouse_state = True
                    __last_mouse_click_time = cur_time

    return None, False
