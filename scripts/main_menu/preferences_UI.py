from __future__ import division

from utils.qt_compat_layer import QtCore, QtGui
from utils.user_settings import settings


class PreferencesDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(PreferencesDialog, self).__init__(parent)
        self.setWindowTitle('Dolag Preferences')
        self.setMinimumWidth(420)
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QtGui.QVBoxLayout(self)

        # Group: Network Editor
        grp_network = QtGui.QGroupBox('Network Editor')
        form_net = QtGui.QFormLayout(grp_network)
        self.sb_snap_dist = QtGui.QSpinBox()
        self.sb_snap_dist.setRange(1, 200)
        form_net.addRow('Snap Distance', self.sb_snap_dist)
        layout.addWidget(grp_network)

        # Group: Quick Console
        grp_console = QtGui.QGroupBox('Quick Console')
        form_con = QtGui.QFormLayout(grp_console)
        self.sb_max_history = QtGui.QSpinBox()
        self.sb_max_history.setRange(1, 500)
        form_con.addRow('Max History Command', self.sb_max_history)
        layout.addWidget(grp_console)

        # Group: Interaction
        grp_inter = QtGui.QGroupBox('Interaction')
        layout_inter = QtGui.QVBoxLayout(grp_inter)
        self.cb_enable_link_ops = QtGui.QCheckBox('Enable Ctrl+Alt to move wire, Shift+Ctrl to duplicate wire')
        layout_inter.addWidget(self.cb_enable_link_ops)
        layout.addWidget(grp_inter)

        # Buttons
        btns = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _load(self):
        # defaults
        snap = int(settings.get('network', 'snap_distance', 10))
        max_hist = int(settings.get('console', 'max_history', 50))
        link_ops = bool(settings.get('interaction', 'enable_link_ops', True))
        self.sb_snap_dist.setValue(snap)
        self.sb_max_history.setValue(max_hist)
        self.cb_enable_link_ops.setChecked(link_ops)

    def accept(self):
        settings.set('network', 'snap_distance', int(self.sb_snap_dist.value()))
        settings.set('console', 'max_history', int(self.sb_max_history.value()))
        settings.set('interaction', 'enable_link_ops', bool(self.cb_enable_link_ops.isChecked()))
        super(PreferencesDialog, self).accept()


def open_preferences():
    dlg = PreferencesDialog()
    (getattr(dlg, 'exec', None) or getattr(dlg, 'exec_', None))()


