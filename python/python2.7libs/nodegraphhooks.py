"""
    intercept event in Network editor
"""
import math
import time

from canvaseventtypes import *
from nodegraphconsole import KeyEventHandler

__last_mouse_state = False
__last_mouse_click_time = 0
__mouse_double_click_delta_time = 0.4

# Ctrl + Space to summon hot console
def createEventHandler(uievent, pending_actions):
    # for quick menu
    if isinstance(uievent, KeyboardEvent) and \
            uievent.eventtype == 'keyhit' and \
            uievent.key == 'Ctrl+Space':
        event_handler = KeyEventHandler(uievent)
        return event_handler, True if event_handler is not None else False

    # for quick teleport
    elif isinstance(uievent, MouseEvent) and \
            uievent.eventtype == 'mousedown':
        global __last_mouse_state
        global __last_mouse_click_time
        global __mouse_double_click_delta_time
        import hou

        nodes = hou.selectedNodes()

        cur_time = time.time()
        delta_time = time.time() - __last_mouse_click_time

        # time out
        if delta_time > __mouse_double_click_delta_time:
            __last_mouse_state = False
            __last_mouse_click_time = 0

        for node in nodes:
            if node.type().name() == 'Dolag_portal':
                # double click
                if __last_mouse_state and delta_time <= __mouse_double_click_delta_time:
                    node.parm("teleport").pressButton()
                    __last_mouse_state = False
                    __last_mouse_click_time = 0

                # first time
                elif not __last_mouse_state:
                    __last_mouse_state = True
                    __last_mouse_click_time = cur_time

    return None, False

