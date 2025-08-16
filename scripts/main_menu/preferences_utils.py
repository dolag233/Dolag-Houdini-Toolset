from __future__ import division

from utils.user_settings import settings


class Config(object):
    class Network(object):
        # (section, key, default)
        SNAP_DISTANCE = ('network', 'snap_distance', 10)

    class Console(object):
        MAX_HISTORY = ('console', 'max_history', 50)

    class Interaction(object):
        ENABLE_LINK_OPS = ('interaction', 'enable_link_ops', True)


def getSetting(section_or_entry, name=None, default=None):
    """Generic accessor for preferences with defaults.

    Usage:
      - getSetting(Config.Network.SNAP_DISTANCE)
      - getSetting('network', 'snap_distance', 10)
    """
    try:
        if name is None and isinstance(section_or_entry, tuple):
            section, key = section_or_entry[0], section_or_entry[1]
            defv = section_or_entry[2] if len(section_or_entry) >= 3 else default
            return settings.get(section, key, defv)
        return settings.get(section_or_entry, name, default)
    except Exception:
        # fallback to provided default for robustness
        if name is None and isinstance(section_or_entry, tuple):
            return section_or_entry[2] if len(section_or_entry) >= 3 else default
        return default


