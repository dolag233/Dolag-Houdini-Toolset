# -*- coding: utf-8 -*-

import hou
import os
from Dolag import node as dn
from Dolag import path as dp


# return the new hda file path. return (node, old_hda_name, old_hda_path, new_hda_name, new_hda_path)
def saveHDACopy(node, suffix="_Copy", save_original_hda=False):
    if isinstance(node, list) or isinstance(node, tuple):
        if len(node) > 1:
            hou.ui.setStatusMessage("Error: Support only one hda node")
            return  # support only one node
        else:
            node = node[0]

    if node is None:
        hou.ui.setStatusMessage("Error: No selected node")
        return

    hda_def = node.type().definition()
    hda_path = hda_def.libraryFilePath()
    hda_folder = os.path.dirname(hda_path)
    hda_name = hda_def.nodeTypeName()

    if save_original_hda and hda_def:
        # save hda first
        hda_def.updateFromNode(node)

    hda_suffix = hda_path[-4:]

    # if can't find hda definition
    if hda_def is None:
        hou.ui.setStatusMessage("Error: Cannot find hda definition")

    new_hda_file_name = hda_name + suffix
    # 对于带版本的hda，名称需要有特殊的处理
    namespaces = hda_name.split("::")
    if len(namespaces) > 2:
        try:
            float(namespaces[-1])  # 判断是否为版本号
            namespaces[-2] += suffix
            new_hda_file_name = "::".join(namespaces)
        except:
            pass

    new_hda_path = "{0}/{1}{2}".format(hda_folder, new_hda_file_name, hda_suffix)

    hou.ui.setStatusMessage("Save a copy {0} in {1}".format(new_hda_file_name, new_hda_path))
    hda_def.copyToHDAFile(new_hda_path, hda_name, new_hda_file_name)
    return node, hda_name, hda_path, hda_name, new_hda_path


def saveHDACopyUnlock(node, save_original_hda=False):
    old_node, old_hda_name, old_hda_path, new_hda_name, new_hda_path = saveHDACopy(node, "_Unlock", save_original_hda)
    hda_category = hou.sopNodeTypeCategory()
    if new_hda_path is not None and os.path.exists(new_hda_path):
        # @TODO not only SOP
        hou.hda.installFile(new_hda_path, force_use_assets=True)
        hda_def = hou.hdaDefinition(hda_category, new_hda_name, new_hda_path)
        hda_type_name = old_node.type().definition().nodeTypeName()
        new_node = old_node.parent().createNode(hda_type_name)
        dn.unlockCustomNode(new_node)
        hda_def = hou.hdaDefinition(hda_category, new_hda_name, new_hda_path)
        hda_def.updateFromNode(new_node)
        # restore
        new_node.destroy()
        hou.hda.uninstallFile(new_hda_path)
        hou.hda.installFile(old_hda_path, force_use_assets=True)
