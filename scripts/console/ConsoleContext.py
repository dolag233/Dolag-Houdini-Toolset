class ConsoleContext(object):
    def __init__(self):
        self.__data = {"selected_nodes": (),
                       "selected_items" : (),
                       "hit_item": None,  # item under your mouse in this network
                       "screen_pos": (0, 0),  # mouse pos in your screen(not the screen pos of network editor)
                       "editor_pos": (0, 0),  # mouse pos in network editor space
                       "editor": None,  # network editor object
                       "qt_keys": 0,  # pressed keys in qt format, use QtCore.Qt.Key_* to access
                       "network_node": None  # current network node
                       }

    def __getitem__(self, key):
        if key not in self.__data.keys():
            raise
        return self.__data[key]

    def __setitem__(self, key, value):
        if key not in self.__data.keys():
            raise
        self.__data[key] = value

    def __str__(self):
        return str(self.__data)

    def __repr__(self):
        class_str = super(ConsoleContext, self).__repr__
        return str(class_str) + "\n" + str(self.__data)
