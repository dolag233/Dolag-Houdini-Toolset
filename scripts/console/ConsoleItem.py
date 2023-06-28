import platform
import time

if platform.python_version_tuple()[0] == '2':
    from ConsoleContext import ConsoleContext

elif platform.python_version_tuple()[0] == '3':
    from .ConsoleContext import ConsoleContext

import hou
from abc import ABCMeta, abstractmethod


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
        self.LUT = time.time()

    def run(self, context):
        if not isinstance(context, ConsoleContext):
            return
        if self.callback is None:
            return

        try:
            self.callback(context)
        except Exception:
            pass

