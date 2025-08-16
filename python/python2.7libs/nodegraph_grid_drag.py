from __future__ import division
import hou
from main_menu.preferences_utils import getSetting
from main_menu.preference_config import Keys
from canvaseventtypes import MouseEvent
from nodegraphbase import EventHandler


class GridDragHandler(EventHandler):
    def __init__(self, uievent, target):
        super(GridDragHandler, self).__init__(uievent)
        self._target = target
        self._undos_group = hou.undos.group("Snap to Grid")
        self._undos_group.__enter__()

    @staticmethod
    def _pick_node_under_cursor(uievent, radius=1.0):
        try:
            editor = uievent.editor
            pos = editor.posFromScreen(uievent.mousepos)
            best = 1e9
            pick = None
            for it in editor.pwd().allItems():
                if isinstance(it, hou.Node):
                    d = (it.position() - pos).length()
                    if d < best and d <= radius:
                        best = d; pick = it
            return pick, pos
        except Exception:
            return None, None

    @classmethod
    def try_begin(cls, uievent):
        if not isinstance(uievent, MouseEvent) or not uievent.mousestate.mmb:
            return None
        node, _ = cls._pick_node_under_cursor(uievent)
        if node is None:
            return None
        handler = cls(uievent, node)
        return handler

    def handleEvent(self, uievent, pending_actions):
        if not isinstance(uievent, MouseEvent) or not uievent.mousestate.mmb:
            return None
        try:
            node = self._target
            # snap to grid
            gx = getSetting(Keys.Network.DRAG_SNAP_DISTANCE_X)
            gy = getSetting(Keys.Network.DRAG_SNAP_DISTANCE_Y)
            editor = uievent.editor
            pos = editor.posFromScreen(uievent.mousepos)
            new_x = pos.x() - node.size().x() / 2
            new_y = pos.y() - node.size().y() / 2
            new_x = round(new_x / gx) * gx
            new_y = round(new_y / gy) * gy
            node.setPosition(hou.Vector2(new_x, new_y))
            return self
        except Exception:
            return None
        
    def end(self):
        del self._undos_group
        self._undos_group = None

