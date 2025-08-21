from __future__ import division

from _utils.user_settings import settings
from main_menu.preference_config import registry

def getSetting(section_or_entry):
    """Generic accessor for preferences with defaults.

    Usage:
      - getSetting(Config.Network.SNAP_DISTANCE)
      - getSetting('network', 'snap_distance', 10)
    """
    if isinstance(section_or_entry, tuple):
        section, key = section_or_entry[0], section_or_entry[1]
        default = registry.get(section, key).default
        setting_data = settings.get(section, key, default)
        if setting_data is not None:
            dtype = registry.get(section, key).dtype
            if dtype is bool:
                return bool(setting_data)
            elif dtype is int:
                return int(setting_data)
            elif dtype is float:
                return float(setting_data)
            elif dtype is str:
                return str(setting_data)
            else:
                return setting_data
        else:
            return default
