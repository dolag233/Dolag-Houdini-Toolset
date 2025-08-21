from __future__ import division
import hou
import json
import os
import traceback
import platform

if platform.python_version_tuple()[0] == '2':
    from ConsoleItem import ConsoleItem
    from ConsoleItemCustom import CUSTOM_ITEMS

elif platform.python_version_tuple()[0] == '3':
    from .ConsoleItem import ConsoleItem
    from .ConsoleItemCustom import CUSTOM_ITEMS
    
from _utils.user_settings import settings


def createNodeTemplate(node_name):
    def callback(context):
        editor = context["editor"]
        # such as "/obj/geo1"
        network = context["network_node"]
        if network is not None and \
                isinstance(network, hou.Node) and \
                network.isNetwork():
            new_node = network.createNode(node_name)
            new_node_pos = context["editor_pos"]
            new_node_size = new_node.size()
            new_node_pos = (new_node_pos[0] - new_node_size[0] / 2, new_node_pos[1] - new_node_size[1] / 2)
            new_node.move(new_node_pos)

    return callback


class ItemCollect(object):
    def __init__(self):
        self.items = {}
        self.item_path = "{0}/scripts/console/console_items.json".format(hou.getenv("DOLAG_PATH"))
        self.loadItem()
        # Restore recent usage order (last 50 item names)
        try:
            recent = settings.get_raw('console_recent', []) or []
            base = 1
            for name in recent:
                it = self.items.get(name)
                if it is not None:
                    it.LUT = base
                    base += 1
        except Exception:
            pass

    def getItems(self):
        return self.items

    def __getitem__(self, key):
        if key not in self.items.keys():
            return None
        return self.items[key]

    def __iter__(self):
        return self.items.__iter__()

    def keys(self):
        return self.items.keys()

    def values(self):
        return self.items.values()

    def update(self, another_dict):
        self.items.update(another_dict)

    def _loadUserCustomItems(self):
        try:
            import sys
            houdini_user_pref = hou.expandString("$HOUDINI_USER_PREF_DIR")
            user_data_path = os.path.join(houdini_user_pref, "DolagPlugin", "user_data")
            
            if user_data_path not in sys.path:
                sys.path.insert(0, user_data_path)
            
            from UserCustomConsoleItems import USER_CUSTOM_ITEMS
            with open(os.path.join(user_data_path, "user_console_items.json"), "r") as f:
                user_custom_template_items = json.load(f)
                
            return USER_CUSTOM_ITEMS, user_custom_template_items
            
        except Exception as e:
            hou.ui.displayMessage("Failed to load UserCustomConsoleItems.py:\n" + str(e))
            return [], []

    def loadItem(self):
        try:
            json_array = []
            if os.path.isfile(self.item_path):
                with open(self.item_path) as f:
                    try:
                        json_array = json.load(f)
                    except:
                        pass

            user_custom_items, user_custom_template_items = self._loadUserCustomItems()
            json_array.extend(user_custom_template_items)
            
            for item in json_array:
                if "node_name" in item.keys():
                    item = ConsoleItem(item_name=item["item_name"], alias=item["alias"], \
                                    callback=createNodeTemplate(item["node_name"]), important=item["important"])
                    self.items[item.item_name] = item

                else:
                    continue

            for item in user_custom_items + CUSTOM_ITEMS:
                self.items[item.item_name] = item
            # keep settings unchanged here; updates happen on execution side

        except Exception as e:
            hou.ui.displayMessage(traceback.format_exc())

    def reload(self):
        self.loadItem()
