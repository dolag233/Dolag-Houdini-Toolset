"""
    duplicate a new node as the reference of the original node
    on changing the original parameter will change the new parameter in the same time
"""
import hou


def copyNodeRef(node):
    # if input node path
    if isinstance(node, str):
        node = hou.node(node)
    # if input is a node instance
    elif isinstance(node, hou.Node):
        pass
    else:
        return

    # copy parm paths into clipboard
    # data structure is as follow:
    # node_path\nparm_path1\nparm_path2...
    tar = node.path()
    for parm in node.parms():
        tar += "\n{0}".format(parm.path())

    hou.ui.copyTextToClipboard(tar)


def pasteNodeRef(node):
    import Dolag
    # if input node path
    if isinstance(node, str):
        node = hou.node(node)
    # if input is a node instance
    elif isinstance(node, hou.Node):
        pass
    else:
        return

    tar = hou.ui.getTextFromClipboard()
    tar = tar.split('\n')
    if len(tar) == 0:
        return

    src_node = hou.node(tar[0])
    if src_node is None:
        return

    # discard tar[0]
    tar = tar[1:]
    # if node types are not the same
    if src_node.type() != node.type():
        return

    parms = node.parms()
    for i in range(len(tar)):
        src_parm = hou.parm(tar[i])
        # skip folder
        if isinstance(src_parm.parmTemplate(), hou.FolderSetParmTemplate) or\
                isinstance(src_parm.parmTemplate(), hou.FolderParmTemplate):
            continue

        # set proper reference expression
        relative_path = Dolag.path.getRelativePath(parms[i].path(), src_parm.path())
        if isinstance(parms[i].parmTemplate(), hou.RampParmTemplate):
            parms[i].setExpression('chramp("{0}")'.format(relative_path), hou.exprLanguage.Hscript)
        elif isinstance(parms[i].parmTemplate(), hou.StringParmTemplate):
            parms[i].setExpression('chs("{0}")'.format(relative_path), hou.exprLanguage.Hscript)
        else:
            parms[i].setExpression('ch("{0}")'.format(relative_path), hou.exprLanguage.Hscript)


def dupNodeRef(node):
    net_node = None
    # if input node path
    if isinstance(node, str):
        node = hou.node(node)
        net_node = node.parent()
    # if input is a node instance
    elif isinstance(node, hou.Node):
        net_node = node.parent()
    # if input node tuple or list
    elif isinstance(node, tuple) or isinstance(node, list):
        for n in node:
            if isinstance(n, hou.Node):
                net_node = n.parent()
    else:
        return

    if net_node is None:
        return

    if isinstance(node, tuple) or isinstance(node, list):
        real_nodes = []
        for n in node:
            if isinstance(n, hou.Node):
                real_nodes.append(n)

        node = tuple(real_nodes)

    else:
        node = (node, )

    # deep copy
    if len(node) != 0:
        net_node.copyItems(node, True)

