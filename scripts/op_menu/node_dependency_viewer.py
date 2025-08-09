"""
Minimal dependency viewer using only hou.hscript('opdepend -d -l 1 <node>').
- Depth = 1: show only direct upstream/downstream within current network
- Depth > 1: layered DFS; draw only adjacent-level edges
"""
import re
import os
import math
import hou
from PySide2 import QtCore
from PySide2 import QtWidgets as QtGui
from PySide2 import QtGui as QtG


class GraphicsView(QtGui.QGraphicsView):
    def __init__(self, scene, parent=None):
        super(GraphicsView, self).__init__(scene, parent)
        self.setRenderHint(QtG.QPainter.Antialiasing)
        self.setDragMode(QtGui.QGraphicsView.NoDrag)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
        self._panning = False
        self._last_pos = None
        try:
            grad = QtG.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(0, 1))
            grad.setCoordinateMode(QtG.QGradient.ObjectBoundingMode)
            grad.setColorAt(0.0, QtG.QColor(54, 58, 61))
            grad.setColorAt(1.0, QtG.QColor(42, 45, 48))
            self.setBackgroundBrush(QtG.QBrush(grad))
        except Exception:
            pass

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        factor = 1.2 if delta > 0 else 1.0 / 1.2
        self.scale(factor, factor)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self._panning = True
            self._last_pos = event.pos()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            event.accept()
            return
        super(GraphicsView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning and self._last_pos is not None:
            delta = event.pos() - self._last_pos
            self._last_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return
        super(GraphicsView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self._panning = False
            self._last_pos = None
            self.setCursor(QtCore.Qt.ArrowCursor)
            event.accept()
            return
        super(GraphicsView, self).mouseReleaseEvent(event)


class GraphNodeItem(QtGui.QGraphicsRectItem):
    def __init__(self, rect, node, label, color, viewer, is_self=False):
        super(GraphNodeItem, self).__init__(rect)
        self.node = node
        self.viewer = viewer
        self._is_self = bool(is_self)
        pen = QtG.QPen(QtG.QColor(color))
        pen.setWidthF(1.2)
        self.setPen(pen)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        # No icon drawing (SVG/hicon and embedded HDA icons vary by build)
        text_offset_x = 8
        self.label_item = QtGui.QGraphicsTextItem(label, self)
        self.label_item.setDefaultTextColor(QtG.QColor('#222'))
        self.label_item.setPos(rect.x() + text_offset_x, rect.y() + 6)

    def center_pos(self):
        r = self.rect()
        return QtCore.QPointF(r.x() + r.width() / 2.0, r.y() + r.height() / 2.0)

    def mousePressEvent(self, event):
        super(GraphNodeItem, self).mousePressEvent(event)
        if self.viewer:
            self.viewer._on_graph_node_clicked(self.node)

    def mouseDoubleClickEvent(self, event):
        super(GraphNodeItem, self).mouseDoubleClickEvent(event)
        if self.viewer:
            self.viewer._on_graph_node_double_clicked(self.node)

    def paint(self, painter, option, widget=None):
        r = self.rect()
        painter.setRenderHint(QtG.QPainter.Antialiasing, True)
        grad = QtG.QLinearGradient(r.topLeft(), r.bottomLeft())
        grad.setColorAt(0.0, QtG.QColor('#fbfbfb'))
        grad.setColorAt(1.0, QtG.QColor('#ededed'))
        painter.setBrush(QtG.QBrush(grad))
        pen = QtG.QPen(QtG.QColor('#c8c8c8'))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawRoundedRect(r, 6, 6)
        # selection highlight
        if self.isSelected() and not self._is_self:
            sel = QtG.QPen(QtG.QColor('#4c9aff'))
            sel.setWidthF(2.0)
            painter.setPen(sel)
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawRoundedRect(r.adjusted(0.7, 0.7, -0.7, -0.7), 6, 6)
        if self._is_self:
            hi = QtG.QPen(QtG.QColor('#f9c74f'))
            hi.setWidthF(2.2)
            hi.setJoinStyle(QtCore.Qt.RoundJoin)
            painter.setPen(hi)
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawRoundedRect(r.adjusted(0.7, 0.7, -0.7, -0.7), 6, 6)


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


def _add_edge(scene, p_start, p_end, color_hex, z=-1):
    color = QtG.QColor(color_hex)
    pen = QtG.QPen(color)
    pen.setWidthF(1.6)
    pen.setCapStyle(QtCore.Qt.RoundCap)
    pen.setJoinStyle(QtCore.Qt.RoundJoin)
    path = QtG.QPainterPath(p_start)
    dx = (p_end.x() - p_start.x())
    ctrl = abs(dx) * 0.35
    c1 = QtCore.QPointF(p_start.x() + ctrl, p_start.y())
    c2 = QtCore.QPointF(p_end.x() - ctrl, p_end.y())
    path.cubicTo(c1, c2, p_end)
    item = scene.addPath(path, pen)
    item.setZValue(z)
    angle = math.atan2(p_end.y() - c2.y(), p_end.x() - c2.x())
    size = 7.0
    p_base = p_end
    p_l = QtCore.QPointF(
        p_base.x() - size * math.cos(angle - math.pi / 6.0),
        p_base.y() - size * math.sin(angle - math.pi / 6.0),
    )
    p_r = QtCore.QPointF(
        p_base.x() - size * math.cos(angle + math.pi / 6.0),
        p_base.y() - size * math.sin(angle + math.pi / 6.0),
    )
    poly = QtG.QPolygonF([p_base, p_l, p_r])
    arrow = scene.addPolygon(poly, QtG.QPen(QtCore.Qt.NoPen), QtG.QBrush(color))
    arrow.setZValue(z)
    return item, arrow


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
        self.scene = QtGui.QGraphicsScene()
        self.view = GraphicsView(self.scene)
        graph_tab = QtGui.QWidget()
        graph_layout = QtGui.QVBoxLayout(graph_tab)
        graph_layout.addWidget(self.view)
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

    def _populate_graph_flat(self, upstream_nodes, downstream_nodes):
        self.scene.clear()
        w = max(self.width(), 780)
        h = max(self.height(), 560)
        margin = 40
        node_h = 36
        v_gap = 14
        fm = QtG.QFontMetrics(self.font())
        def text_w(text):
            try:
                return fm.width(text)
            except Exception:
                return len(text) * 8
        out_w = max([text_w(self._display_name(n)) for n in upstream_nodes] + [120]) + 24
        in_w = max([text_w(self._display_name(n)) for n in downstream_nodes] + [120]) + 24
        self_text = self._node.name()
        self_w = min(max(text_w(self_text) + 28, 200), 520)
        col_x = {'out': margin, 'self': (w - self_w) / 2.0, 'in': w - margin - in_w}
        def layout_y(count):
            if count == 0:
                return []
            total_h = count * node_h + (count - 1) * v_gap
            start_y = (h - total_h) / 2.0
            return [start_y + i * (node_h + v_gap) for i in range(count)]
        out_ys = layout_y(len(upstream_nodes))
        in_ys = layout_y(len(downstream_nodes))

        center_y = h / 2.0 - node_h / 2.0
        create = lambda x, y, wbox, text, color, obj, s=False: self.scene.addItem(GraphNodeItem(QtCore.QRectF(x, y, wbox, node_h), obj, text, color, self, s)) or self.scene.items()[-1]
        create(col_x['self'], center_y, self_w, self_text, '#8ecae6', self._node, True)

        for i, n in enumerate(upstream_nodes):
            item = GraphNodeItem(QtCore.QRectF(col_x['out'], out_ys[i], out_w, node_h), n, self._display_name(n), '#bde0fe', self)
            self.scene.addItem(item)
            p_start = QtCore.QPointF(col_x['out'] + out_w, out_ys[i] + node_h / 2.0)
            p_end = QtCore.QPointF(col_x['self'], center_y + node_h / 2.0)
            _add_edge(self.scene, p_start, p_end, '#6f7a9b', z=-1)

        for i, n in enumerate(downstream_nodes):
            item = GraphNodeItem(QtCore.QRectF(col_x['in'], in_ys[i], in_w, node_h), n, self._display_name(n), '#cdeac0', self)
            self.scene.addItem(item)
            p_start = QtCore.QPointF(col_x['self'] + self_w, center_y + node_h / 2.0)
            p_end = QtCore.QPointF(col_x['in'], in_ys[i] + node_h / 2.0)
            _add_edge(self.scene, p_start, p_end, '#6a9b7a', z=-1)

        items_rect = self.scene.itemsBoundingRect().adjusted(-24, -24, 24, 24)
        self.view.setSceneRect(items_rect)
        self.view.fitInView(items_rect, QtCore.Qt.KeepAspectRatio)

    def _populate_graph_layered(self, up_layers, up_edges, down_layers, down_edges):
        self.scene.clear()
        node_h = 36
        v_gap = 14
        col_gap = 40
        fm = QtG.QFontMetrics(self.font())
        def text_w(text):
            try:
                return fm.width(text)
            except Exception:
                return len(text) * 8
        self_text = self._node.name()
        self_w = min(max(text_w(self_text) + 28, 200), 520)

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

        up_widths = [(max([text_w(self._display_name(n)) for n in layer] + [120]) + 24) if layer else 120 for layer in up_layers]
        down_widths = [(max([text_w(self._display_name(n)) for n in layer] + [120]) + 24) if layer else 120 for layer in down_layers]
        x_self = 0.0
        up_xs = []
        acc = x_self - col_gap
        for w_col in up_widths:
            acc -= w_col
            up_xs.append(acc)
            acc -= col_gap
        down_xs = []
        acc = x_self + self_w + col_gap
        for w_col in down_widths:
            down_xs.append(acc)
            acc += w_col + col_gap
        def layout_y(count):
            if count == 0:
                return []
            total_h = count * node_h + (count - 1) * v_gap
            start_y = - total_h / 2.0
            return [start_y + i * (node_h + v_gap) for i in range(count)]
        node_to_item = {}
        def create_item(x, y, w_box, text, color, node_obj, is_self=False):
            rect = QtCore.QRectF(x, y, w_box, node_h)
            item = GraphNodeItem(rect, node_obj, text, color, self, is_self=is_self)
            item.setZValue(1)
            self.scene.addItem(item)
            node_to_item[node_obj.path()] = item
            return item
        center_y = - node_h / 2.0
        create_item(x_self, center_y, self_w, self_text, '#8ecae6', self._node, True)
        for idx, layer in enumerate(up_layers):
            if not layer:
                continue
            x_col = up_xs[idx]
            w_col = up_widths[idx]
            ys = layout_y(len(layer))
            for i, n in enumerate(layer):
                create_item(x_col, ys[i], w_col, self._display_name(n), '#bde0fe', n)
        for idx, layer in enumerate(down_layers):
            if not layer:
                continue
            x_col = down_xs[idx]
            w_col = down_widths[idx]
            ys = layout_y(len(layer))
            for i, n in enumerate(layer):
                create_item(x_col, ys[i], w_col, self._display_name(n), '#cdeac0', n)
        def edge_points(src_item, dst_item):
            r1 = src_item.rect()
            r2 = dst_item.rect()
            p_start = QtCore.QPointF(r1.x() + r1.width(), r1.y() + r1.height() / 2.0)
            p_end = QtCore.QPointF(r2.x(), r2.y() + r2.height() / 2.0)
            return p_start, p_end
        for src, dst in up_edges:
            si = node_to_item.get(src.path())
            di = node_to_item.get(dst.path())
            if si and di:
                p_start, p_end = edge_points(si, di)
                _add_edge(self.scene, p_start, p_end, '#6f7a9b', z=-1)
        for src, dst in down_edges:
            si = node_to_item.get(src.path())
            di = node_to_item.get(dst.path())
            if si and di:
                p_start, p_end = edge_points(si, di)
                _add_edge(self.scene, p_start, p_end, '#6a9b7a', z=-1)
        items_rect = self.scene.itemsBoundingRect().adjusted(-24, -24, 24, 24)
        self.view.setSceneRect(items_rect)
        self.view.fitInView(items_rect, QtCore.Qt.KeepAspectRatio)

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


def open_dependency_viewer(node):
    from utils import show_UI
    real_node = node if isinstance(node, hou.Node) else hou.node(str(node))
    if real_node is None:
        return
    show_UI.showUIStandalone(DependencyViewer, real_node)


