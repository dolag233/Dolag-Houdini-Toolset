import hou
import os
from Dolag import node as dn
from Dolag import path as dp


# simply copy and rename the hda to $DOLAG_PATH/otls/alias
def setHdaAlias(node, new_hda_menu_name):
    node = dn.getNode(node)
    if node is None:
        return

    hda_name = node.type().name()
    hda_path = dp.getHdaLibraryPath(hda_name)
    # if cannot find this otl
    if hda_path is None:
        return

    hda_def = hou.hdaDefinition(hou.sopNodeTypeCategory(), hda_name, hda_path)
    # if can't find hda definition
    if hda_def is None:
        hou.ui.setStatusMessage("Error: Cannot find hda definition")

    suffix = hda_path[-4:]
    hda_folder = '/'.join(hda_path.split('/')[:-1])
    new_hda_file_name = hda_name + "_alias"
    alias_folder = hou.getenv("DOLAG_PATH") + "/otls/alias"
    new_hda_path = "{0}/{1}{2}".format(alias_folder, new_hda_file_name, suffix)
    # if already exist this file, then increase
    while True:
        if os.path.isfile(new_hda_path):
            new_hda_path = dp.increaseFileName(new_hda_path)
        else:
            break

    hou.ui.setStatusMessage("Save alias {0} in {1}, will be valid after restarting".format(new_hda_menu_name, new_hda_path))
    hda_def.copyToHDAFile(new_hda_path, hda_name, new_hda_menu_name)
