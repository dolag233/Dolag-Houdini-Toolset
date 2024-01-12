"""
    intercept event in Network editor
"""
import time

from canvaseventtypes import *
from nodegraphconsole import KeyEventHandler
from nodegraphexchanger import ExchangerHandler
from nodegraphduplicator import DuplicatorHandler

__last_mouse_state = False
__last_mouse_click_time = 0
__mouse_double_click_delta_time = 0.4
__last_alt_state = False


# Ctrl + Space to summon hot console
def createEventHandler(uievent, pending_actions):
    # for quick menu
    if isinstance(uievent, KeyboardEvent) and \
            uievent.eventtype == 'keyhit' and \
            uievent.key == 'Ctrl+Space':
        event_handler = KeyEventHandler(uievent)
        return event_handler, True if event_handler is not None else False

    # for quick teleport
    if isinstance(uievent, MouseEvent) and \
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

    # Exchanger
    if isinstance(uievent, MouseEvent) and \
            uievent.mousestate.lmb and \
            uievent.modifierstate.alt and uievent.modifierstate.ctrl and not uievent.modifierstate.shift:
        event_handler = ExchangerHandler(uievent)
        return event_handler, True if event_handler is not None else False

    # Duplicator
    elif isinstance(uievent, MouseEvent) and \
            uievent.mousestate.lmb and \
            uievent.modifierstate.shift and uievent.modifierstate.ctrl and not uievent.modifierstate.alt:
        event_handler = DuplicatorHandler(uievent)
        return event_handler, True if event_handler is not None else False

    return None, False
