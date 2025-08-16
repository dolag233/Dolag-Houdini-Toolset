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
        return cls(uievent, node)

    def handleEvent(self, uievent, pending_actions):
        if not isinstance(uievent, MouseEvent):
            return None
        if not uievent.mousestate.mmb:
            return None
        try:
            node, pos = self._pick_node_under_cursor(uievent)
            if node is None:
                node = self._target
            # snap to grid
            gx = max(1, int(getSetting(Keys.Network.SNAP_DISTANCE_X)))
            gy = max(1, int(getSetting(Keys.Network.SNAP_DISTANCE_Y)))
            new_x = round(pos.x() / gx) * gx
            new_y = round(pos.y() / gy) * gy
            node.setPosition(hou.Vector2(new_x, new_y))
            return self
        except Exception:
            return None


