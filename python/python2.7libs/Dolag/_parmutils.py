import hou
import json


# get parm from str or hou.Parm
def getParm(parm_desc):
    parm = None
    # if input parm path
    if isinstance(parm_desc, str):
        parm = hou.parm(parm_desc)

    # if input is a parm instance
    elif isinstance(parm_desc, hou.Parm):
        parm = parm_desc

    else:
        pass

    return parm


# serialize parameter value
def serializeParameterValue2Json(node):
    # if input node path
    if isinstance(node, str):
        node = hou.node(node)
    # if input is a node instance
    elif isinstance(node, hou.Node):
        pass
    else:
        return

    # serialize parameters
    parms_json = dict()
    parms = node.parms()
    # parms = [ [parm, False] for parm in parms] # [parm_data, is_traveled]
    for parm in parms:
        # just copy value and expression
        parm_json = dict()
        pt = parm.parmTemplate()
        parm_json['name'] = parm.name()
        parm_json['type'] = str(pt.type())
        parm_json['label'] = pt.label()
        # not support ramp now
        if isinstance(pt, hou.RampParmTemplate):
            continue

        # int, multiparm block, ordered menu and toggle value
        elif (isinstance(pt, hou.FolderParmTemplate) and pt.folderType() == hou.folderType.MultiparmBlock)\
                or (isinstance(pt, hou.IntParmTemplate) and pt.numComponents() == 1) or isinstance(pt, hou.ToggleParmTemplate)\
                or isinstance(pt, hou.MenuParmTemplate):
            parm_json['value'] = parm.evalAsInt()

        # int vector value
        elif isinstance(pt, hou.IntParmTemplate) and pt.numComponents() > 1:
            if hasattr(parm, 'evalAsInts'):
                parm_json['value'] = parm.evalAsInts()
            elif hasattr(parm, 'evalAsInt'):
                parm_json['value'] = parm.evalAsInt()
            else:
                continue

        # float value
        elif isinstance(pt, hou.FloatParmTemplate) and pt.numComponents() == 1:
            parm_json['value'] = parm.evalAsFloat()

        # vector value
        elif isinstance(pt, hou.FloatParmTemplate) and pt.numComponents() > 1:
            if hasattr(parm, 'evalAsFloats'):
                parm_json['value'] = parm.evalAsFloats()
            elif hasattr(parm, 'evalAsFloat'):
                parm_json['value'] = parm.evalAsFloat()
            else:
                continue

        # string value
        elif isinstance(pt, hou.StringParmTemplate):
            parm_json['value'] = parm.rawValue()

        else:
            continue

        parms_json[parm.name()] = parm_json

    json_str = json.dumps(parms_json, indent=4, ensure_ascii=False) # @TODO maybe not supported in python2
    return json_str


# parse json to parameter value
def parseJson2ParameterValue(node, json_str):
    # if input node path
    if isinstance(node, str):
        node = hou.node(node)
    # if input is a node instance
    elif isinstance(node, hou.Node):
        pass
    else:
        return

    try:
        parms_json = json.loads(json_str)
    except Exception as e:
        print("Error when parse json file: " + e)
        return

    parms = node.parms()
    with hou.undos.group("Parse json to parameter value"):
        for parm in parms:
            if parm.name() in parms_json.keys():
                parm.set(parms_json[parm.name()]['value'])

