import hou


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
