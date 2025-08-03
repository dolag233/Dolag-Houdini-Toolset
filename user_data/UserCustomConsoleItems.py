'''
    Custom user quick console items
'''
import hou
import platform
from console.ConsoleItem import ConsoleItem

# USER_CUSTOM_ITEMS contains all user customized console item here
# you can simply create ConsoleItem object and append to USER_CUSTOM_ITEMS
USER_CUSTOM_ITEMS = []

'''
    Below here are some examples
'''
# # merge selected nodes
# def merge_selected_cb(context):
#     if len(context["selected_nodes"]) > 0:
#         network = context["network_node"]
#         merge_node = network.createNode("merge")
#         index = 0
#         for node in context["selected_nodes"]:
#             for i in range(len(node.outputNames())):
#                 merge_node.setInput(index, node, i)
#                 index += 1

#         merge_node.setPosition(context["editor_pos"])


# tmp_item = ConsoleItem(item_name="Merge Selected", alias="merge", callback=merge_selected_cb)
# USER_CUSTOM_ITEMS.append(tmp_item)

# # switch selected nodes
# def switch_selected_cb(context):
#     if len(context["selected_nodes"]) > 0:
#         network = context["network_node"]
#         switch_node = network.createNode("switch")
#         index = 0
#         for node in context["selected_nodes"]:
#             for i in range(len(node.outputNames())):
#                 switch_node.setInput(index, node, i)
#                 index += 1

#         switch_node.setPosition(context["editor_pos"])


# tmp_item = ConsoleItem(item_name="Switch Selected", alias="switch", callback=switch_selected_cb)
# USER_CUSTOM_ITEMS.append(tmp_item)
