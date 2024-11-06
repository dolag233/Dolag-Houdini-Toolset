import hou
import json


# get node from str or hou.Node
def getNode(node_desc, node_type=hou.Node):
    node = None
    # if input node path
    if isinstance(node_desc, str):
        node = hou.node(node_desc)

    # if node_type is not tuple
    elif (not isinstance(node_type, tuple)) and isinstance(node_desc, node_type):
        node = node_desc

    elif isinstance(node_type, tuple):
        for nt in node_type:
            if isinstance(node_desc, nt):
                node = node_desc

    else:
        pass

    return node


def unlockCustomNode(cur_node, traveled_nodes=None):
    import os
    if traveled_nodes is None:
        traveled_nodes = []

    cur_node.allowEditingOfContents()
    for n in cur_node.children():
        if not isinstance(n, hou.SopNode) or n.type() is None or n.type().definition() is None:
            continue

        node_type = n.type()
        hda_def = n.type().definition()
        hda_path = hda_def.libraryFilePath()
        if (hda_path == "Embedded" or not os.path.exists(hda_path)\
            or not os.path.abspath(hou.getenv("HFS")) in os.path.abspath(hda_path)) and n not in traveled_nodes:
            n.allowEditingOfContents()
            traveled_nodes.append(n)
            unlockCustomNode(n, traveled_nodes)


# serialize node metadata json
def serializeNodeMetadata2Json(node):
    node = getNode(node)

    # serialize node metadata
    meta_json = dict()
    meta_json['type'] = node.type().name()
    meta_json['name'] = node.name()
    meta_json['pos'] = list(node.position())
    meta_json['shape'] = node.userData('nodeshape')
    if meta_json['shape'] is None:
        meta_json['shape'] = node.type().defaultShape()
    meta_json['color'] = node.color().rgb()
    meta_json['input_nodes'] = [c.inputItem().name() for c in node.inputConnections()]
    meta_json['output_nodes'] = [c.outputItem().name() for c in node.outputConnections()]
    return json.dumps(meta_json, indent=4, ensure_ascii=False)  # @TODO maybe not supported in python2


# parse node metadata json
def parseJson2NodeMetadata(node, node_json):
    with hou.undos.group("Parse json to node metadata"):
        node = getNode(node)
        node.setName(node_json['name'])
        node.setPosition(node_json['pos'])
        node.setColor(node_json['color'])
        node.setUserData({'nodeshape': node_json['shape']})
        for i in range(len(node_json['input_nodes'])):
            node.setInput(i, hou.item(node_json['input_nodes'][i]))

        for i in range(len(node_json['output_nodes'])):
            node.setOutput(i, hou.item(node_json['output_nodes'][i]))
