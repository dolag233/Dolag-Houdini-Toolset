"""
    Node path copy helpers
    - copyNodePath(node): 复制绝对路径到剪贴板
    - copyRelativeNodePath(node): 复制相对当前 Network 的相对路径到剪贴板
"""
import hou
from Dolag import node as dn


def _get_network_pwd():
    """Return the current NetworkEditor's pwd, or None if not available."""
    try:
        net = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if net is not None:
            return net.pwd()
    except Exception:
        pass
    return None


def copyNodePath(node):
    node = dn.getNode(node)
    if node is None:
        return

    hou.ui.copyTextToClipboard(node.path())


def copyRelativeNodePath(node):
    node = dn.getNode(node)
    if node is None:
        return

    pwd = _get_network_pwd()
    # 若取不到当前 Network，则使用父级作为基准
    if pwd is None:
        pwd = node.parent()
        if pwd is None:
            # 如果连父级都没有，说明是根节点，直接返回节点名
            hou.ui.copyTextToClipboard(node.name())
            return

    try:
        rel_path = pwd.relativePathTo(node)
        # 如果相对路径为空或无效，回退为节点名
        if not rel_path or rel_path == '.':
            rel_path = node.name()
    except Exception:
        # 兜底：回退为节点名
        rel_path = node.name()

    hou.ui.copyTextToClipboard(rel_path)


