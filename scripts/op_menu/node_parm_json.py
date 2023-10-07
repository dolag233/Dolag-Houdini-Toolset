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