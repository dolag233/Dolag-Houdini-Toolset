from canvaseventtypes import *
from nodegraphbase import EventHandler
from nodegraphconsoleUI import ConsoleWindow


# event handler class will not be destroyed because of coroutine
# until handleEvent return None
class KeyEventHandler(EventHandler):
    def __init__(self, uievent):
        super(KeyEventHandler, self).__init__(uievent)
        self.window = ConsoleWindow(hou_event=uievent)

    def getEditorPos(self, uievent):
        return uievent.editor.posFromScreen(uievent.mousepos)

    def handleEvent(self, uievent, pending_actions):
        # if hit ctrl space again
        if isinstance(uievent, KeyboardEvent) and \
                uievent.eventtype == 'keyhit' and \
                uievent.key == 'Ctrl+Space':
            self.window.hou_event = uievent
            self.window.show()
            return self

        # if window has been closed
        elif not self.window.isVisible():
            return None

        # if release keys, finish handler
        elif isinstance(uievent, KeyboardEvent) and \
                uievent.eventtype == 'keydown' and \
                uievent.key in ('Esc', 'Enter'):
            self.window.close()
            return None

        # mouse move will update the uievent sent to window
        elif isinstance(uievent, MouseEvent):
            self.window.hou_event = uievent
            return self

        else:
            self.window.close()
            return None

    def __del__(self):
        self.window.close()
