"""
Minimal dependency viewer using only hou.hscript('opdepend -d -l 1 <node>').
- Depth = 1: show only direct upstream/downstream within current network
- Depth > 1: layered DFS; draw only adjacent-level edges

Rendering is delegated to the shared NodeGraphWidget.
"""
import re
import os
import hou
from PySide2 import QtCore
from PySide2 import QtWidgets as QtGui
from PySide2 import QtGui as QtG
from .node_graph_widget import NodeGraphWidget


# Graph drawing handled by shared NodeGraphWidget


def _run_hscript(cmd):
    try:
        out, err = hou.hscript(cmd)
        return out or ""
    except Exception:
        return ""


def _extract_node_paths(text):
    paths = []
    for line in (text or '').splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('/'):
            paths.append(line.split()[0])
    # dedupe keep order
    seen, uniq = set(), []
    for p in paths:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def _collect_direct_graph(parent_node):
    upstream_of, downstream_of, node_map = {}, {}, {}
    if parent_node is None:
        return upstream_of, downstream_of, node_map
    try:
        nodes = list(parent_node.children())
    except Exception:
        nodes = []
    for n in nodes:
        node_map[n.path()] = n
    for n in nodes:
        try:
            txt = _run_hscript('opdepend -e -i -I -l 1 {}'.format(n.path()))
            srcs = [p for p in _extract_node_paths(txt) if p in node_map and p != n.path()]
            upstream_of[n.path()] = set(srcs)
            for sp in srcs:
                downstream_of.setdefault(sp, set()).add(n.path())
        except Exception:
            continue
    for p in node_map:
        upstream_of.setdefault(p, set())
        downstream_of.setdefault(p, set())
    return upstream_of, downstream_of, node_map


# Edges are drawn inside NodeGraphWidget


def _build_layers(center_node, depth, upstream_of, downstream_of, node_map):
    depth = max(1, int(depth))
    c = center_node.path()
    # upstream
    up_lvl = {c: 0}
    up_edges = set()
    stack = [(c, 0)]
    while stack:
        cur, lv = stack.pop()
        if lv >= depth:
            continue
        for s in upstream_of.get(cur, set()):
            if s not in node_map or s == cur:
                continue
            nl = lv + 1
            if up_lvl.get(s) is None or nl < up_lvl.get(s, 9999):
                up_lvl[s] = nl
                stack.append((s, nl))
            up_edges.add((s, cur))
    up_layers = []
    for d in range(1, depth + 1):
        ls = [node_map[p] for p, lv in up_lvl.items() if lv == d]
        ls.sort(key=lambda n: n.path())
        up_layers.append(ls)
    up_edges_adj = []
    for sp, dp in up_edges:
        ls = up_lvl.get(sp)
        ld = 0 if dp == c else up_lvl.get(dp)
        if ls is not None and ((dp == c and ls == 1) or (ld is not None and ls == ld + 1)):
            up_edges_adj.append((node_map[sp], node_map.get(dp, center_node)))

    # downstream
    down_lvl = {c: 0}
    down_edges = set()
    stack = [(c, 0)]
    while stack:
        cur, lv = stack.pop()
        if lv >= depth:
            continue
        for d in downstream_of.get(cur, set()):
            if d not in node_map or d == cur:
                continue
            nl = lv + 1
            if down_lvl.get(d) is None or nl < down_lvl.get(d, 9999):
                down_lvl[d] = nl
                stack.append((d, nl))
            down_edges.add((cur, d))
    down_layers = []
    for d in range(1, depth + 1):
        ls = [node_map[p] for p, lv in down_lvl.items() if lv == d]
        ls.sort(key=lambda n: n.path())
        down_layers.append(ls)
    down_edges_adj = []
    for sp, dp in down_edges:
        ls = 0 if sp == c else down_lvl.get(sp)
        ld = down_lvl.get(dp)
        if ld is not None and ((sp == c and ld == 1) or (ls is not None and ld == ls + 1)):
            down_edges_adj.append((node_map.get(sp, center_node), node_map[dp]))

    return up_layers, up_edges_adj, down_layers, down_edges_adj


class DependencyViewer(QtGui.QDialog):
    def __init__(self, node, parent=None):
        super(DependencyViewer, self).__init__(parent)
        flags = self.windowFlags()
        flags = flags & ~QtCore.Qt.WindowContextHelpButtonHint
        flags |= QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setWindowTitle("Dependency Viewer - {}".format(node.path()))
        self.setMinimumSize(780, 560)
        self._node = node
        self._depth = 1
        self._did_position = False
        self._build_ui()
        self._populate()

    def _build_ui(self):
        main_layout = QtGui.QVBoxLayout(self)
        header = QtGui.QHBoxLayout()
        self.info_label = QtGui.QLabel("")
        header.addWidget(self.info_label)
        header.addStretch(1)
        # Refresh button
        self.btn_refresh = QtGui.QToolButton()
        self.btn_refresh.setText("Refresh")
        self.btn_refresh.setToolTip("Rebuild references from currently selected node(s)")
        header.addWidget(self.btn_refresh)
        header.addWidget(QtGui.QLabel("Depth"))
        self.depth_spin = QtGui.QSpinBox()
        self.depth_spin.setRange(1, 8)
        self.depth_spin.setValue(1)
        self.depth_spin.setFixedWidth(60)
        header.addWidget(self.depth_spin)
        self.auto_focus_chk = QtGui.QCheckBox("Auto Focus")
        self.auto_focus_chk.setChecked(True)
        header.addWidget(self.auto_focus_chk)
        # Always on top toggle
        self.on_top_chk = QtGui.QCheckBox("Always On Top")
        self.on_top_chk.setChecked(True)
        header.addWidget(self.on_top_chk)
        main_layout.addLayout(header)

        self.tabs = QtGui.QTabWidget()
        self.graph = NodeGraphWidget()
        # Hook events
        self.graph.on_click = self._on_graph_node_clicked
        self.graph.on_dbl = self._on_graph_node_double_clicked
        self.graph.on_selection_changed = self._on_graph_selection_changed
        graph_tab = QtGui.QWidget()
        graph_layout = QtGui.QVBoxLayout(graph_tab)
        graph_layout.addWidget(self.graph)
        self.tabs.addTab(graph_tab, "Graph")

        list_tab = QtGui.QWidget()
        list_layout = QtGui.QVBoxLayout(list_tab)
        splitter = QtGui.QSplitter()
        splitter.setOrientation(QtCore.Qt.Horizontal)

        left_container = QtGui.QWidget()
        left_layout = QtGui.QVBoxLayout(left_container)
        left_title = QtGui.QLabel("Dependencies (Upstream)")
        self.list_out = QtGui.QListWidget()
        left_layout.addWidget(left_title)
        left_layout.addWidget(self.list_out)

        right_container = QtGui.QWidget()
        right_layout = QtGui.QVBoxLayout(right_container)
        right_title = QtGui.QLabel("Dependents (Downstream)")
        self.list_in = QtGui.QListWidget()
        right_layout.addWidget(right_title)
        right_layout.addWidget(self.list_in)

        splitter.addWidget(left_container)
        splitter.addWidget(right_container)
        list_layout.addWidget(splitter)
        self.tabs.addTab(list_tab, "List")

        main_layout.addWidget(self.tabs)

        self.list_out.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_in.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.depth_spin.valueChanged.connect(self._on_depth_changed)
        self.on_top_chk.stateChanged.connect(self._on_on_top_changed)
        self.list_out.itemSelectionChanged.connect(self._on_list_selection_changed)
        self.list_in.itemSelectionChanged.connect(self._on_list_selection_changed)
        self.btn_refresh.clicked.connect(self._refresh_from_network)

    def _populate(self):
        upstream_of, downstream_of, node_map = _collect_direct_graph(self._node.parent())
        c = self._node.path()

        direct_up = [node_map[p] for p in sorted(upstream_of.get(c, set())) if p in node_map]
        direct_down = [node_map[p] for p in sorted(downstream_of.get(c, set())) if p in node_map]

        # List tab
        self.list_out.clear()
        for n in direct_up:
            item = QtGui.QListWidgetItem(self._display_name(n))
            item.setData(QtCore.Qt.UserRole, n)
            self.list_out.addItem(item)
        self.list_in.clear()
        for n in direct_down:
            item = QtGui.QListWidgetItem(self._display_name(n))
            item.setData(QtCore.Qt.UserRole, n)
            self.list_in.addItem(item)

        self.info_label.setText("Dependencies: {}    Dependents: {}".format(len(direct_up), len(direct_down)))

        if self._depth <= 1:
            self._populate_graph_flat(direct_up, direct_down)
        else:
            up_layers, up_edges, down_layers, down_edges = _build_layers(self._node, self._depth, upstream_of, downstream_of, node_map)
            self._populate_graph_layered(up_layers, up_edges, down_layers, down_edges)
        # Sync graph selection with current Network Editor selection
        self._sync_graph_selection_from_network()

    def _populate_graph_flat(self, upstream_nodes, downstream_nodes):
        # Build single-layer data and render via shared widget
        up_layers = [upstream_nodes] if upstream_nodes else []
        down_layers = [downstream_nodes] if downstream_nodes else []
        up_edges = [(n, self._node) for n in upstream_nodes]
        down_edges = [(self._node, n) for n in downstream_nodes]
        self.graph.render_layered(self._node, up_layers, up_edges, down_layers, down_edges, self._display_name)

    def _populate_graph_layered(self, up_layers, up_edges, down_layers, down_edges):
        # Reorder layers first to honor parent order rule, then render via shared widget

        # Reorder each layer based on parent order from previous layer
        def reorder_layers(prev_index, layers, edges, edges_are_parent_to_child):
            ordered_layers = []
            for layer_nodes in layers:
                # Compute key per node using parents' indices in prev layer
                keys = {}
                for n in layer_nodes:
                    parents = []
                    if edges_are_parent_to_child:
                        for s, d in edges:
                            if d == n and s.path() in prev_index:
                                parents.append(prev_index[s.path()])
                    else:
                        for s, d in edges:
                            if s == n and d.path() in prev_index:
                                parents.append(prev_index[d.path()])
                    if not parents:
                        parents = [0]
                    keys[n.path()] = (min(parents), sum(parents) / float(len(parents)), self._display_name(n))
                layer_sorted = sorted(layer_nodes, key=lambda nn: keys[nn.path()])
                for i, n in enumerate(layer_sorted):
                    prev_index[n.path()] = i
                ordered_layers.append(layer_sorted)
            return ordered_layers

        down_prev = {self._node.path(): 0}
        down_layers = reorder_layers(down_prev, down_layers, down_edges, True)
        up_prev = {self._node.path(): 0}
        up_layers = reorder_layers(up_prev, up_layers, up_edges, False)

        # Render
        self.graph.render_layered(self._node, up_layers, up_edges, down_layers, down_edges, self._display_name)

    def _on_item_double_clicked(self, item):
        n = item.data(QtCore.Qt.UserRole)
        self._recenter_to_node(n)

    def _on_depth_changed(self, val):
        self._depth = max(1, int(val))
        self._populate()

    def _on_on_top_changed(self, state):
        flags = self.windowFlags()
        if state == QtCore.Qt.Checked:
            flags |= QtCore.Qt.WindowStaysOnTopHint
        else:
            flags &= ~QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()  # re-apply flags

    def _on_graph_node_double_clicked(self, node):
        self._recenter_to_node(node)

    def _on_graph_node_clicked(self, node):
        # Select corresponding item in lists and focus in network if enabled
        try:
            if self.auto_focus_chk.isChecked():
                self._frame_in_network(node)
        except Exception:
            pass

    def _on_graph_selection_changed(self, nodes):
        try:
            if not self.auto_focus_chk.isChecked():
                return
            if len(nodes) == 1 and isinstance(nodes[0], hou.Node):
                self._frame_in_network(nodes[0])
        except Exception:
            pass

    def _on_list_selection_changed(self):
        try:
            if not self.auto_focus_chk.isChecked():
                return
            cur = self.list_out.currentItem() or self.list_in.currentItem()
            if not cur:
                return
            n = cur.data(QtCore.Qt.UserRole)
            if isinstance(n, hou.Node):
                self._frame_in_network(n)
        except Exception:
            pass

    def _frame_in_network(self, node):
        try:
            net = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
            if net is None:
                return
            net.setPwd(node.parent())
            for s in hou.selectedNodes():
                s.setSelected(False)
            node.setSelected(True)
            net.homeToSelection()
        except Exception:
            pass

    def _recenter_to_node(self, node):
        if not isinstance(node, hou.Node):
            return
        self._node = node
        self.setWindowTitle("Dependency Viewer - {}".format(node.path()))
        self._populate()

    # -------- helpers --------
    def _display_name(self, n):
        try:
            if n.parent() == self._node.parent():
                return n.name()
            base = self._node.parent().path()
            p = n.path()
            if p.startswith(base + '/'):
                return p[len(base)+1:]
            return p
        except Exception:
            return n.path()

    def showEvent(self, event):
        super(DependencyViewer, self).showEvent(event)
        try:
            if not self._did_position:
                self._did_position = True
                pos = QtGui.QCursor.pos()
                geo = self.frameGeometry()
                geo.moveCenter(pos)
                self.move(geo.topLeft())
        except Exception:
            pass

    # ----- helpers for selection sync / refresh -----
    def _sync_graph_selection_from_network(self):
        try:
            sels = hou.selectedNodes()
            paths = [n.path() for n in sels]
            self.graph.select_by_paths(paths)
        except Exception:
            pass

    def _refresh_from_network(self):
        try:
            sels = hou.selectedNodes()
            if len(sels) >= 1:
                self._recenter_to_node(sels[0])
            else:
                self._populate()
            # After populate, select all selected nodes in graph as well
            self._sync_graph_selection_from_network()
        except Exception:
            self._populate()


def open_dependency_viewer(node):
    from utils import show_UI
    real_node = node if isinstance(node, hou.Node) else hou.node(str(node))
    if real_node is None:
        return
    show_UI.showUIStandalone(DependencyViewer, real_node)


