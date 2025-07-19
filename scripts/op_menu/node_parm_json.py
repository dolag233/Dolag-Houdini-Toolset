"""
    copy and paste node as json
"""
import hou
from Dolag import parm as pm, node as nd


def copyNodeMetadataJson(node):
    hou.ui.copyTextToClipboard(nd.serializeNodeMetadata2Json(node))

def copyParameterValueJson(node):
    hou.ui.copyTextToClipboard(pm.serializeParameterValue2Json(node))

def copyNodeMetadataAndParameterValueJson(node):
    node_json = dict()
    node_json['node'] = nd.serializeNodeMetadata2Json(node)
    node_json['parameters'] = pm.serializeParameterValue2Json(node)
    hou.ui.copyTextToClipboard(node_json)

# def pasteNodeMetadataFromJson(node):
#     json_str = hou.ui.pasteTextFromClipboard()
#     nd.parseJson2NodeMetadata(node, json_str)

def pasteParameterValueFromJson(node):
    json_str = hou.ui.getTextFromClipboard()
    pm.parseJson2ParameterValue(node, json_str)

# def pasteNodeMetadataAndParameterValueFromJson(node):
#     json_str = hou.ui.pasteTextFromClipboard()
#     node_json = json.loads(json_str)
#     nd.parseJson2NodeMetadata(node, node_json['node'])
#     pm.parseJson2ParameterValue(node, node_json['parameters'])