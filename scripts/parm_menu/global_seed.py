"""
    1. copy a numeric param as a global param
    2. paste it to another param, then make it assoicated with the global param
"""
import Dolag
import hou
import random


def copyGlobalParamToClipboard(parm):
    # if not a int or float param
    if not isinstance(parm.parmTemplate(), hou.IntParmTemplate) and not isinstance(parm.parmTemplate(),
                                                                                   hou.FloatParmTemplate):
        return

    parm.copyToParmClipboard()


def pasteGlobalParamFromClipboard(parm):
    # if not a int or float param
    if not isinstance(parm.parmTemplate(), hou.IntParmTemplate) and not isinstance(parm.parmTemplate(),
                                                                                   hou.FloatParmTemplate):
        return

    clip_content = hou.parmClipboardContents()
    if len(clip_content) == 0:
        return

    # get global param
    global_param = clip_content[0]
    global_param_path = global_param["path"]
    global_param = hou.parm(global_param_path)

    # get relative path
    r_path = Dolag.path.getRelativePath(parm.path(), global_param.path())

    # check parm expression
    expression = ''
    try:
        expression = parm.expression()
    except:
        # if do not has expression, set expression direclty
        parm.setExpression(('(hou.parm("{0}").eval() * {1} - {2})').format(r_path, random.random() * 1145, random.random() * 1419), hou.exprLanguage.Python)
        return

    if parm.expressionLanguage() == hou.exprLanguage.Python:
        parm.setExpression(R'(({0}) + (hou.parm("{1}").eval() * {2} - {3}))'.format(expression, r_path, random.random() * 1145,
                                                                       random.random() * 1419), hou.exprLanguage.Python)
    elif parm.expressionLanguage() == hou.exprLanguage.Hscript:
        parm.setExpression(R'(({0}) + (ch("{1}") * {2} - {3}))'.format(expression, r_path, random.random() * 1145,
                                                                       random.random() * 1419), hou.exprLanguage.Hscript)