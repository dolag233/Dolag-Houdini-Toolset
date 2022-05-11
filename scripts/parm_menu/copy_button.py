import Dolag
import hou


def copyButtonToClipboard(parm):
    # if not a button
    if not isinstance(parm.parmTemplate(), hou.ButtonParmTemplate):
        return

    parm.copyToParmClipboard()


# only used to append call pressButton from the copied parm
def pasteButtonFromClipboard(parm):
    # if not a button
    if not isinstance(parm.parmTemplate(), hou.ButtonParmTemplate):
        return

    clipboard = hou.parmClipboardContents()
    # if clipboard tuple isn't right
    if len(clipboard) != 1:
        return

    clipboard_item = clipboard[0]
    ref_parm = hou.parm(clipboard_item["path"])
    # if ref parm is not button type
    if ref_parm is None and not isinstance(ref_parm.parmTemplate(), hou.ButtonParmTemplate):
        return

    # if paste to the same parm
    if id(ref_parm) == id(parm):
        return

    # button parm cannot be animated so can't get expression if not set
    try:
        # get expr of ref_parm and strip "return"
        pre_expr = ref_parm.expression().replace("\nreturn", '').replace("return", '')
        pre_expr = '' if pre_expr == '' else pre_expr + '\n'

    except:
        pre_expr = ''

    # if already exist
    for line in pre_expr.split('\n'):
        if parm.path() in line:
            return

    # get relative path
    r_path = Dolag.path.getRelativePath(ref_parm.path(), parm.path())
    ref_parm.setExpression(pre_expr + "hou.parm('{0}').pressButton()\nreturn".format(r_path), hou.exprLanguage.Python)
