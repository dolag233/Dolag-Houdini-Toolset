"""
    intercept event in Network editor
"""
import time

from canvaseventtypes import *
from nodegraphconsole import KeyEventHandler
from nodegraphexchanger import ExchangerHandler
from nodegraphduplicator import DuplicatorHandler
from main_menu.preferences_utils import getSetting
from main_menu.preference_config import Keys
from nodegraph_grid_drag import GridDragHandler
__grid_drag_active = None

__last_mouse_state = False
__last_mouse_click_time = 0
__mouse_double_click_delta_time = 0.2
__last_alt_state = False


# Ctrl + Space to summon hot console
def createEventHandler(uievent, pending_actions):
    # for quick menu
    if isinstance(uievent, KeyboardEvent) and \
            uievent.eventtype == 'keyhit' and \
            uievent.key == 'Ctrl+Space':
        event_handler = KeyEventHandler(uievent)
        return event_handler, True if event_handler is not None else False

    # Ctrl + R to open Dependency Viewer on first selected node
    if isinstance(uievent, KeyboardEvent) and \
            uievent.eventtype == 'keyhit' and \
            (uievent.key == 'Ctrl+R' or uievent.key == 'Ctrl+r'):
        try:
            import hou
            from op_menu import node_dependency_viewer
            sel = hou.selectedNodes()
            if len(sel) > 0:
                node_dependency_viewer.open_dependency_viewer(sel[0])
        except Exception:
            # fail silently to avoid interrupting Houdini event loop
            pass
        return None, True

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

    if bool(getSetting(Keys.Network.ENABLE_LINK_OPS)):
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

    # Grid-drag on MMB: emulate drag by tracking between mousedown & mouseup
    if bool(getSetting(Keys.Network.ENABLE_GRID_DRAG)) and isinstance(uievent, MouseEvent):
        global __grid_drag_active
        if uievent.eventtype == 'mousedown' and uievent.mousestate.mmb and uievent.modifierstate.alt:
            h = GridDragHandler.try_begin(uievent)
            if h is not None:
                __grid_drag_active = h
                return h, True
        elif uievent.eventtype == 'mousemove' and __grid_drag_active is not None:
            h = __grid_drag_active.handleEvent(uievent, pending_actions)
            if h is not None:
                __grid_drag_active = h
                return h, True
            else:
                __grid_drag_active.end()
                __grid_drag_active = None

        elif uievent.eventtype == 'mouseup':
            if __grid_drag_active is not None:
                __grid_drag_active.end()
                __grid_drag_active = None

    return None, False
