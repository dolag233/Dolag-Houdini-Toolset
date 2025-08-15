import math
from utils.qt_compat_layer import QtCore, QtGui, QtG, QtSvg


class GraphicsView(QtGui.QGraphicsView):
    def __init__(self, scene, parent=None):
        super(GraphicsView, self).__init__(scene, parent)
        self.setRenderHint(QtG.QPainter.Antialiasing)
        # Rubber band selection with left mouse; middle mouse panning
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        # Avoid selection ghosting/trails: prefer full viewport refresh, disable cache
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.setCacheMode(QtGui.QGraphicsView.CacheNone)
        try:
            self.setRubberBandSelectionMode(QtCore.Qt.IntersectsItemBoundingRect)
        except Exception:
            pass
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
    def __init__(self, rect, node_obj, text, color, on_click=None, on_dbl=None, is_center=False):
        super(GraphNodeItem, self).__init__(rect)
        self.node_obj = node_obj
        self._on_click = on_click
        self._on_dbl = on_dbl
        self._is_center = bool(is_center)
        pen = QtG.QPen(QtG.QColor(color))
        pen.setWidthF(1.2)
        self.setPen(pen)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        self.label_item = QtGui.QGraphicsTextItem(text, self)
        self.label_item.setDefaultTextColor(QtG.QColor('#222'))
        self.label_item.setPos(rect.x() + 8, rect.y() + 6)
        try:
            effect = QtGui.QGraphicsDropShadowEffect()
            effect.setBlurRadius(8)
            effect.setOffset(0, 1)
            effect.setColor(QtG.QColor(0, 0, 0, 60))
            self.setGraphicsEffect(effect)
        except Exception:
            pass

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
        if self.isSelected():
            sel = QtG.QPen(QtG.QColor('#4c9aff'))
            sel.setWidthF(2.5)
            painter.setPen(sel)
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawRoundedRect(r.adjusted(0.7, 0.7, -0.7, -0.7), 6, 6)
        # center node no special yellow border (per new spec)

    def mousePressEvent(self, event):
        super(GraphNodeItem, self).mousePressEvent(event)
        if callable(self._on_click):
            self._on_click(self.node_obj)

    def mouseDoubleClickEvent(self, event):
        super(GraphNodeItem, self).mouseDoubleClickEvent(event)
        if callable(self._on_dbl):
            self._on_dbl(self.node_obj)


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


class NodeGraphWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(NodeGraphWidget, self).__init__(parent)
        self.scene = QtGui.QGraphicsScene()
        self.view = GraphicsView(self.scene)
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.on_click = None
        self.on_dbl = None
        self._node_to_item = {}
        try:
            self.scene.selectionChanged.connect(self._on_scene_selection_changed)
        except Exception:
            pass
        # Shortcuts
        try:
            QtGui.QShortcut(QtGui.QKeySequence('Ctrl+A'), self, activated=self.select_all)
            QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Shift+A'), self, activated=self.clear_selection)
        except Exception:
            pass

    def fit(self):
        items_rect = self.scene.itemsBoundingRect().adjusted(-24, -24, 24, 24)
        self.view.setSceneRect(items_rect)
        self.view.fitInView(items_rect, QtCore.Qt.KeepAspectRatio)

    def clear(self):
        self.scene.clear()
        self._node_to_item = {}

    def render_layered(self, center_node, up_layers, up_edges, down_layers, down_edges, display_name):
        self.scene.clear()
        node_h = 36
        v_gap = 14
        col_gap = 40
        fm = QtG.QFontMetrics(self.font())
        def text_w(text):
            try:
                return fm.horizontalAdvance(text)
            except Exception:
                return fm.width(text)
        self_text = display_name(center_node)
        self_w = min(max(text_w(self_text) + 28, 200), 520)
        up_widths = [(max([text_w(display_name(n)) for n in layer] + [120]) + 24) if layer else 120 for layer in up_layers]
        down_widths = [(max([text_w(display_name(n)) for n in layer] + [120]) + 24) if layer else 120 for layer in down_layers]
        x_self = 0.0
        up_xs, acc = [], x_self - col_gap
        for w_col in up_widths:
            acc -= w_col
            up_xs.append(acc)
            acc -= col_gap
        down_xs, acc = [], x_self + self_w + col_gap
        for w_col in down_widths:
            down_xs.append(acc)
            acc += w_col + col_gap
        def layout_y(count):
            if count == 0:
                return []
            total_h = count * node_h + (count - 1) * v_gap
            start_y = - total_h / 2.0
            return [start_y + i * (node_h + v_gap) for i in range(count)]
        def create_item(x, y, w_box, text, color, node_obj, is_center=False):
            rect = QtCore.QRectF(x, y, w_box, node_h)
            item = GraphNodeItem(rect, node_obj, text, color,
                                 on_click=getattr(self, 'on_click', None),
                                 on_dbl=getattr(self, 'on_dbl', None),
                                 is_center=is_center)
            item.setZValue(1)
            self.scene.addItem(item)
            key = getattr(node_obj, 'path', lambda: id(node_obj))()
            self._node_to_item[key] = item
            return item
        center_y = - node_h / 2.0
        create_item(x_self, center_y, self_w, self_text, '#8ecae6', center_node, True)
        for idx, layer in enumerate(up_layers):
            if not layer:
                continue
            x_col = up_xs[idx]; w_col = up_widths[idx]
            ys = layout_y(len(layer))
            for i, n in enumerate(layer):
                create_item(x_col, ys[i], w_col, display_name(n), '#bde0fe', n)
        for idx, layer in enumerate(down_layers):
            if not layer:
                continue
            x_col = down_xs[idx]; w_col = down_widths[idx]
            ys = layout_y(len(layer))
            for i, n in enumerate(layer):
                create_item(x_col, ys[i], w_col, display_name(n), '#cdeac0', n)
        def edge_points(src_item, dst_item):
            r1 = src_item.rect(); r2 = dst_item.rect()
            p_start = QtCore.QPointF(r1.x() + r1.width(), r1.y() + r1.height() / 2.0)
            p_end = QtCore.QPointF(r2.x(), r2.y() + r2.height() / 2.0)
            return p_start, p_end
        for src, dst in up_edges:
            si = self._node_to_item.get(src.path()); di = self._node_to_item.get(dst.path())
            if si and di:
                p_start, p_end = edge_points(si, di)
                _add_edge(self.scene, p_start, p_end, '#6f7a9b', z=-1)
        for src, dst in down_edges:
            si = self._node_to_item.get(src.path()); di = self._node_to_item.get(dst.path())
            if si and di:
                p_start, p_end = edge_points(si, di)
                _add_edge(self.scene, p_start, p_end, '#6a9b7a', z=-1)
        self.fit()

    # ------- forest rendering (multiple independent trees side-by-side) -------
    def render_forest(self, trees, display_name, orientation='horizontal'):
        """Render multiple trees side-by-side.
        trees: list of tuples (center_node, down_layers, down_edges)
        """
        self.clear()
        x_offset = 0.0
        y_offset = 0.0
        spacing = 80.0

        for center_node, down_layers, down_edges in trees:
            width_used, height_used = self._render_one_tree(center_node, down_layers, down_edges, display_name, x_offset, y_offset)
            if orientation == 'vertical':
                y_offset += height_used + spacing
            else:
                x_offset += width_used + spacing
        self.fit()

    def _render_one_tree(self, center_node, down_layers, down_edges, display_name, x_offset=0.0, y_offset=0.0):
        # Returns width used for this tree
        node_h = 36
        v_gap = 14
        col_gap = 40
        fm = QtG.QFontMetrics(self.font())
        def text_w(text):
            try:
                return fm.horizontalAdvance(text)
            except Exception:
                return fm.width(text)

        self_text = display_name(center_node)
        self_w = min(max(text_w(self_text) + 28, 200), 520)
        down_widths = [(max([text_w(display_name(n)) for n in layer] + [120]) + 24) if layer else 120 for layer in down_layers]

        x_self = x_offset
        down_xs, acc = [], x_self + self_w + col_gap
        for w_col in down_widths:
            down_xs.append(acc)
            acc += w_col + col_gap

        # Vertical metrics for this tree (overall height based on widest column)
        max_count = max([len(layer) for layer in down_layers] + [1])
        total_h = max_count * node_h + (max_count - 1) * v_gap
        def layout_y(count):
            if count == 0:
                return []
            # Top-aligned to y_offset, each column uses same top so trees stack cleanly
            return [y_offset + i * (node_h + v_gap) for i in range(count)]

        def create_item(x, y, w_box, text, color, node_obj, is_center=False):
            rect = QtCore.QRectF(x, y, w_box, node_h)
            item = GraphNodeItem(rect, node_obj, text, color,
                                 on_click=getattr(self, 'on_click', None),
                                 on_dbl=getattr(self, 'on_dbl', None),
                                 is_center=is_center)
            item.setZValue(1)
            self.scene.addItem(item)
            key = getattr(node_obj, 'path', lambda: id(node_obj))()
            self._node_to_item[key] = item
            return item

        center_y = y_offset + (total_h / 2.0) - (node_h / 2.0)
        create_item(x_self, center_y, self_w, self_text, '#8ecae6', center_node, True)
        for idx, layer in enumerate(down_layers):
            if not layer:
                continue
            x_col = down_xs[idx]
            w_col = down_widths[idx]
            ys = layout_y(len(layer))
            for i, n in enumerate(layer):
                create_item(x_col, ys[i], w_col, display_name(n), '#cdeac0', n)

        def edge_points(src_item, dst_item):
            r1 = src_item.rect(); r2 = dst_item.rect()
            p_start = QtCore.QPointF(r1.x() + r1.width(), r1.y() + r1.height() / 2.0)
            p_end = QtCore.QPointF(r2.x(), r2.y() + r2.height() / 2.0)
            return p_start, p_end
        for src, dst in down_edges:
            si = self._node_to_item.get(src.path()); di = self._node_to_item.get(dst.path())
            if si and di:
                p_start, p_end = edge_points(si, di)
                _add_edge(self.scene, p_start, p_end, '#6a9b7a', z=-1)

        total_width = (down_xs[-1] + down_widths[-1] - x_self) if down_xs else self_w
        total_height = max(total_h, node_h)
        return total_width, total_height
    

        # ---- selection utilities ----
    def selected_nodes(self):
        result = []
        for key, item in self._node_to_item.items():
            try:
                if item.isSelected():
                    result.append(item.node_obj)
            except Exception:
                pass
        return result

    def clear_selection(self):
        for item in self._node_to_item.values():
            try:
                item.setSelected(False)
            except Exception:
                pass

    def select_all(self):
        for item in self._node_to_item.values():
            try:
                item.setSelected(True)
            except Exception:
                pass

    def select_by_paths(self, paths):
        sset = set(paths or [])
        for key, item in self._node_to_item.items():
            try:
                item.setSelected(key in sset)
            except Exception:
                pass

    def _on_scene_selection_changed(self):
        # expose selection to parent via optional callback attribute
        cb = getattr(self, 'on_selection_changed', None)
        if callable(cb):
            try:
                cb(self.selected_nodes())
            except Exception:
                pass


def _make_pin_icon(color_hex):
    try:
        if QtSvg is None:
            return None
        path_d = "M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z"
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16">'
        svg += '<path fill="%s" d="%s"/>' % (color_hex, path_d)
        svg += '</svg>'
        data = QtCore.QByteArray(svg.encode('utf-8'))
        renderer = QtSvg.QSvgRenderer(data)
        pm = QtG.QPixmap(16, 16)
        pm.fill(QtCore.Qt.transparent)
        painter = QtG.QPainter(pm)
        renderer.render(painter)
        painter.end()
        return QtG.QIcon(pm)
    except Exception:
        return None


# ---------- utility embedded in NodeGraphWidget ----------
class _TitlePinButton(QtGui.QToolButton):
    def __init__(self, window):
        super(_TitlePinButton, self).__init__(window)
        self._window = window
        self.setToolTip('Always on top')
        self.setCheckable(True)
        self.setAutoRaise(True)
        self.setFixedSize(22, 18)
        self.setIconSize(QtCore.QSize(16, 16))
        self.clicked.connect(self._toggle_pin)
        # default ON
        self._set_on_top(True)
        self._apply_state()

    def _is_on_top(self):
        return bool(self._window.windowFlags() & QtCore.Qt.WindowStaysOnTopHint)

    def _set_on_top(self, on):
        flags = self._window.windowFlags()
        if on:
            flags |= QtCore.Qt.WindowStaysOnTopHint
        else:
            flags &= ~QtCore.Qt.WindowStaysOnTopHint
        self._window.setWindowFlags(flags)
        self._window.show()

    def _apply_state(self):
        on = self._is_on_top()
        self.setChecked(on)
        icon = _make_pin_icon('#f0a500' if on else '#c8c8c8')
        if icon is not None:
            self.setIcon(icon)
        else:
            self.setText('*')

    def _toggle_pin(self):
        self._set_on_top(not self._is_on_top())
        self._apply_state()
