"""
    save project file Incrementally
    in the File menu
"""
from hou import hipFile as hf
from Dolag import path as dp


def saveIncrease():
    # proj name with suffix
    name = hf.basename()
    # strip suffix
    if ".hip" == name[-4:]:
        pass
    elif ".hipnc" == name[-6:]:
        # if is hip non-commercial
        pass
    else:
        return

    file_name = dp.increaseFileName(name)
    file_name = HIP = hou.getenv("HIP") + '/' + file_name
    try:
        hf.save(file_name)
        hou.ui.setStatusMessage("Save file as {0}".format(file_name))
    except Exception:
        hou.ui.setStatusMessage("Save Failed")


saveIncrease()
