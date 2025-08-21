"""
Unlocked Nodes Viewer
- Recursively scan selected nodes for unlocked HDAs (optionally include subnodes)
- Show in a UI listing; provide Lock/Sync buttons
- Render a simple 1-column graph using shared NodeGraphWidget when needed
"""
import hou
from _utils.qt_compat_layer import QtCore, QtGui

from .node_graph_widget import NodeGraphWidget, _TitlePinButton


def _iter_nodes_recursive(start_nodes, include_children=True):
    seen = set()
    stack = list(start_nodes)
    while stack:
        n = stack.pop()
        if n is None:
            continue
        p = n.path()
        if p in seen:
            continue
        seen.add(p)
        yield n
        if include_children:
            try:
                stack.extend(list(n.allSubChildren()))
            except Exception:
                pass


def _is_unlocked(n):
    try:
        if n.isInsideLockedHDA():
            return False
        otl = n.type().definition()
        if otl is None:
            return False
        return n.isEditable() or not n.isLockedHDA()
    except Exception:
        return False


class UnlockedNodesViewer(QtGui.QDialog):
    def __init__(self, parent=None):
        super(UnlockedNodesViewer, self).__init__(parent)
        flags = self.windowFlags()
        flags = flags & ~QtCore.Qt.WindowContextHelpButtonHint
        flags |= QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)
        self.setMinimumSize(620, 540)
        self.setWindowTitle("Unlocked Nodes Viewer")
        self._include_children = True
        self._build_ui()
        self._refresh()
        # add pin button into toolbar area, right-aligned; default ON handled inside button
        try:
            self._pin_btn = _TitlePinButton(self)
            self._toolbar_right.addWidget(self._pin_btn)
        except Exception:
            pass

    def _build_ui(self):
        layout = QtGui.QVBoxLayout(self)
        toolbar = QtGui.QHBoxLayout()
        self.chk_children = QtGui.QCheckBox("Include Children")
        self.chk_children.setChecked(True)
        toolbar.addWidget(self.chk_children)
        toolbar.addStretch(1)
        self.btn_refresh = QtGui.QPushButton("Refresh")
        self.btn_select_all = QtGui.QPushButton("Select All")
        self.btn_lock_sel = QtGui.QPushButton("Lock Selected")
        toolbar.addWidget(self.btn_refresh)
        toolbar.addWidget(self.btn_select_all)
        toolbar.addWidget(self.btn_lock_sel)
        # keep a tiny right container for pin button injection
        self._toolbar_right = QtGui.QHBoxLayout()
        self._toolbar_right.setContentsMargins(0,0,0,0)
        toolbar.addLayout(self._toolbar_right)
        layout.addLayout(toolbar)

        # Graph-only UI to enable rubber-band multi-select etc.
        self.graph = NodeGraphWidget()
        layout.addWidget(self.graph, 1)
        self.status_label = QtGui.QLabel("")
        layout.addWidget(self.status_label)

        # Events
        self.btn_refresh.clicked.connect(self._refresh)
        self.chk_children.stateChanged.connect(self._on_children_changed)
        self.btn_lock_sel.clicked.connect(self._lock_selected)
        self.btn_select_all.clicked.connect(self._select_all)
        self.graph.on_selection_changed = self._on_graph_selection
        self.graph.on_dbl = self._focus_in_network

    def _refresh(self):
        self._include_children = self.chk_children.isChecked()
        sels = hou.selectedNodes()
        # 支持多选入口：对每个选中的顶层节点构建其解锁子树，然后合并并去重
        all_unlocked = {}
        for root in sels or []:
            sub_nodes = list(_iter_nodes_recursive([root], self._include_children))
            for n in sub_nodes:
                if _is_unlocked(n):
                    all_unlocked[n.path()] = n
        # 若未选择，则在其父网络下扫描一层作为兜底
        if not sels:
            try:
                parent = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor).pwd()
                sub_nodes = list(_iter_nodes_recursive(parent.children(), self._include_children))
                for n in sub_nodes:
                    if _is_unlocked(n):
                        all_unlocked[n.path()] = n
            except Exception:
                pass

        unlocked_map = all_unlocked
        self.graph.clear()
        if unlocked_map:
            # Build a forest: for each selected root, build its unlocked subtree
            forest = []
            roots = sels if sels else [list(unlocked_map.values())[0]]
            def children_of(n):
                try:
                    return [c for c in n.children() if c.path() in unlocked_map]
                except Exception:
                    return []
            visited_global = set()
            for root in roots:
                down_layers, down_edges = [], []
                frontier = [root]
                visited = set([root.path()])
                for _ in range(1, 8):
                    nxt = []
                    for p in frontier:
                        for ch in children_of(p):
                            if ch.path() not in visited:
                                visited.add(ch.path())
                                nxt.append(ch)
                                down_edges.append((p, ch))
                    if not nxt:
                        break
                    down_layers.append(nxt)
                    frontier = nxt
                visited_global.update(visited)
                forest.append((root, down_layers, down_edges))
            # Remaining unlocked nodes not connected from any selected root: append as extra small trees
            for p, n in unlocked_map.items():
                if p not in visited_global:
                    forest.append((n, [], []))
            # Vertical orientation: stack trees from top to bottom
            self.graph.render_forest(forest, lambda x: x.name(), orientation='vertical')
            self.status_label.setText("Unlocked: {} | Selected: {}".format(len(unlocked_map), len(self.graph.selected_nodes())))
        else:
            self.status_label.setText("No unlocked nodes found in current selection.")

    def _on_children_changed(self, _):
        self._refresh()

    def _lock_selected(self):
        for n in self.graph.selected_nodes():
            try:
                n.allowEditingOfContents(False)
                n.matchCurrentDefinition()
            except Exception:
                pass
        self._refresh()

    def _select_all(self):
        try:
            self.graph.select_all()
        except Exception:
            pass

    def _focus_in_network(self, n):
        try:
            net = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
            if net:
                net.setPwd(n.parent())
                for s in hou.selectedNodes():
                    s.setSelected(False)
                n.setSelected(True)
                net.homeToSelection()
        except Exception:
            pass

    def _on_graph_selection(self, nodes):
        try:
            self.status_label.setText("Selected: {}".format(len(nodes)))
        except Exception:
            pass


def open_unlocked_nodes_viewer():
    from _utils import show_UI
    show_UI.showUIStandalone(UnlockedNodesViewer)


