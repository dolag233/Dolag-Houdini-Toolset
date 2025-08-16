from __future__ import division

from collections import OrderedDict


class PreferenceItem(object):
    """Definition of one preference item.

    Fields:
      - section: logical section/group key stored in settings (str)
      - key: setting key name (str)
      - label: human-readable label for UI (str)
      - dtype: python type: int | float | bool | str
      - default: default value
      - minimum / maximum: numeric bounds if applicable (optional)
      - group: UI group headline (str)
      - order: sort order within group (int)
    """

    def __init__(self, section, key, label, dtype, default, group, order=0, minimum=None, maximum=None):
        self.section = section
        self.key = key
        self.label = label
        self.dtype = dtype
        self.default = default
        self.minimum = minimum
        self.maximum = maximum
        self.group = group
        self.order = int(order or 0)


class PreferenceRegistry(object):
    """Registry that stores all preference items and provides lookup helpers."""

    def __init__(self):
        self._items = []
        self._by_pair = {}

    def register(self, item):
        key = (item.section, item.key)
        self._by_pair[key] = item
        self._items.append(item)
        return item

    def get(self, section, key):
        return self._by_pair.get((section, key))

    def items(self):
        return list(self._items)

    def grouped(self):
        groups = OrderedDict()
        for it in sorted(self._items, key=lambda x: (x.group, x.order)):
            groups.setdefault(it.group, []).append(it)
        return groups


# Build registry and enum-like keys for usage in code
registry = PreferenceRegistry()


class Keys(object):
    class Network(object):
        SNAP_DISTANCE_X = ('network', 'snap_distance_x')
        SNAP_DISTANCE_Y = ('network', 'snap_distance_y')
        DRAG_SNAP_DISTANCE_X = ('network', 'drag_snap_distance_x')
        DRAG_SNAP_DISTANCE_Y = ('network', 'drag_snap_distance_y')
        ENABLE_LINK_OPS = ('network', 'enable_link_ops')
        ENABLE_GRID_DRAG = ('network', 'enable_grid_drag')

    class Console(object):
        MAX_HISTORY = ('console', 'max_history')


# Define items (labels and defaults)
registry.register(PreferenceItem(
    section='network', key='snap_distance_x', label='Snap Distance X',
    dtype=float, default=1.12, group='Network Editor', order=10, minimum=0, maximum=2,
))
registry.register(PreferenceItem(
    section='network', key='snap_distance_y', label='Snap Distance Y',
    dtype=float, default=0.3, group='Network Editor', order=11, minimum=0, maximum=2,
))
registry.register(PreferenceItem(
    section='network', key='drag_snap_distance_x', label='Drag Snap Distance X',
    dtype=float, default=0.5, group='Network Editor', order=12, minimum=0, maximum=2,
))
registry.register(PreferenceItem(
    section='network', key='drag_snap_distance_y', label='Drag Snap Distance Y',
    dtype=float, default=0.2, group='Network Editor', order=13, minimum=0, maximum=2,
))
registry.register(PreferenceItem(
    section='network', key='enable_link_ops', label='Enable Ctrl+Alt move wire, Shift+Ctrl duplicate wire',
    dtype=bool, default=True, group='Network', order=20,
))
registry.register(PreferenceItem(
    section='network', key='enable_grid_drag', label='Enable MMB grid-drag to snap node while dragging',
    dtype=bool, default=True, group='Network', order=21,
))
registry.register(PreferenceItem(
    section='console', key='max_history', label='Max History Command',
    dtype=int, default=50, group='Quick Console', order=30, minimum=1, maximum=500,
))


