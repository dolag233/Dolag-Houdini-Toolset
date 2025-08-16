import platform
import time
import traceback

if platform.python_version_tuple()[0] == '2':
    from ConsoleContext import ConsoleContext

elif platform.python_version_tuple()[0] == '3':
    from .ConsoleContext import ConsoleContext

import hou
from utils.user_settings import settings
from abc import ABCMeta, abstractmethod

# Global usage counter for LUT (Last Used Time)
# Higher numbers mean more recently used
_global_usage_counter = 0

def get_next_usage_counter():
    """Get next usage counter value (thread-safe increment)"""
    global _global_usage_counter
    _global_usage_counter += 1
    return _global_usage_counter


class ConsoleItemBase(object):
    __metaclass__ = ABCMeta
    item_name = ''
    alias = ''
    important = False
    callback = None

    def __init__(self, item_name, callback, alias=tuple(), important=False):
        # item name must be unique
        # and will be displayed
        self.item_name = item_name
        self.alias = alias
        # important item will be shown when initialization
        self.important = important
        # callback function
        self.callback = callback

    @abstractmethod
    def run(self, context):
        # run self.callback
        pass


# @TODO abstract class
class ConsoleItem(ConsoleItemBase):
    def __init__(self, item_name, callback, alias=tuple(), important=False):
        super(ConsoleItem, self).__init__(item_name=item_name, callback=callback, \
                                          alias=alias, important=important)
        # last used time
        self.LUT = 0

    def updateLastUsedTime(self):
        self.LUT = get_next_usage_counter()

    def run(self, context):
        if not isinstance(context, ConsoleContext):
            return
        if self.callback is None:
            return

        try:
            self.callback(context)
            # persist recent command names (last 50)
            try:
                recent = settings.get_raw('console_recent', []) or []
                name = self.item_name
                if name in recent:
                    recent.remove(name)
                recent.append(name)
                if len(recent) > 50:
                    recent = recent[-50:]
                settings.set_raw('console_recent', recent)
            except Exception:
                pass
        except Exception as e:
            hou.ui.displayMessage(traceback.format_exc())

