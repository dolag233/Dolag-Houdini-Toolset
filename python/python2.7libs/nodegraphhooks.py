"""
    intercept event in Network editor
"""
from canvaseventtypes import *
from nodegraphconsole import KeyEventHandler


# Ctrl + Space to summon hot console
def createEventHandler(uievent, pending_actions):
    if isinstance(uievent, KeyboardEvent) and \
            uievent.eventtype == 'keyhit' and \
            uievent.key == 'Ctrl+Space':
        event_handler = KeyEventHandler(uievent)
        return event_handler, True if event_handler is not None else False

    return None, False
