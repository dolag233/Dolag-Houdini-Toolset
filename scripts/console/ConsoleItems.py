from ConsoleItem import ConsoleItem
from ConsoleContext import ConsoleContext
from ConsoleItemCustom import CUSTOM_ITEMS
import hou
import json
import os


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
        # [0]: item_name [1]: alias [2]: node_name
        node_creation = [("Point Wrangle", "pw", "pointwrangle"),
                         ("Primitive Wrangle", ("prw", "primw"), "primitivewrangle"),
                         ("Attribute Wrangle", "aw", "attributewrangle"),
                         ("Merge", "m", "merge"), ]
        for n in node_creation:
            item = ConsoleItem(item_name=n[0], alias=n[1], callback=createNodeTemplate(n[2]))
            self.items[item.item_name] = item

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

    def loadItem(self):
        try:
            # first load json
            json_array = []
            if os.path.isfile(self.item_path):
                with open(self.item_path) as f:
                    json_array = json.load(f)

            for item in json_array:
                if "node_name" in item.keys():
                    item = ConsoleItem(item_name=item["item_name"], alias=item["alias"], \
                                       callback=createNodeTemplate(item["node_name"]), important=item["important"])
                    self.items[item.item_name] = item

                else:
                    continue

            # second load custom item
            # import importlib
            # importlib.reload(ConsoleItemCustom)
            for item in CUSTOM_ITEMS:
                self.items[item.item_name] = item

        except Exception:
            return

    def reload(self):
        self.loadItem()
