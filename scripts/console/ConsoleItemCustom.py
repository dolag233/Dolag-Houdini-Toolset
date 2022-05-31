"""
    User custom console items
"""
import hou
from ConsoleItem import ConsoleItem

# CUSTOM_ITEMS contains all user customized console item here
# you can simply create ConsoleItem object and append to CUSTOM_ITEMS
CUSTOM_ITEMS = []


# create callback for custom item
# context are defined in ConsoleContext.py
def my_custom_0_cb(context):
    if context["selected_nodes"]:
        msg = "You don't select any node"
        if len(context["selected_nodes"]) > 1:
            msg = "You select " + str(len(context["selected_nodes"])) + " Nodes"
        elif len(context["selected_nodes"]) == 1:
            msg = "You select 1 Node"

        hou.ui.displayMessage(msg)


# create custom item
my_custom_0 = ConsoleItem(item_name="Count Node", alias="cn", callback=my_custom_0_cb)
CUSTOM_ITEMS.append(my_custom_0)
