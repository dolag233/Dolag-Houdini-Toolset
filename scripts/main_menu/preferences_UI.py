from __future__ import division

from utils.qt_compat_layer import QtCore, QtGui
from utils.user_settings import settings
from .preference_config import registry


class PreferencesDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(PreferencesDialog, self).__init__(parent)
        self.setWindowTitle('Dolag Preferences')
        self.setMinimumWidth(420)
        self._build_ui()
        self._load()

    def _build_ui(self):
        layout = QtGui.QVBoxLayout(self)

        # Auto-build groups from config registry
        self._widgets = {}
        groups = registry.grouped()
        for group_name, items in groups.items():
            box = QtGui.QGroupBox(group_name)
            form = QtGui.QFormLayout(box)
            for it in items:
                if it.dtype is bool:
                    w = QtGui.QCheckBox(it.label)
                    form.addRow(w)
                elif it.dtype in (int, float):
                    if it.dtype is int:
                        w = QtGui.QSpinBox()
                        if it.minimum is not None: w.setMinimum(int(it.minimum))
                        if it.maximum is not None: w.setMaximum(int(it.maximum))
                    else:
                        w = QtGui.QDoubleSpinBox()
                        if it.minimum is not None: w.setMinimum(float(it.minimum))
                        if it.maximum is not None: w.setMaximum(float(it.maximum))
                    form.addRow(it.label, w)
                else:
                    w = QtGui.QLineEdit()
                    form.addRow(it.label, w)
                self._widgets[(it.section, it.key)] = w
            layout.addWidget(box)

        # Buttons
        btns = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _load(self):
        for it in registry.items():
            w = self._widgets.get((it.section, it.key))
            if w is None:
                continue
            val = settings.get(it.section, it.key, it.default)
            try:
                if it.dtype is bool:
                    w.setChecked(bool(val))
                elif it.dtype is int:
                    w.setValue(int(val))
                elif it.dtype is float:
                    w.setValue(float(val))
                else:
                    w.setText(str(val))
            except Exception:
                if it.dtype is bool:
                    w.setChecked(bool(it.default))
                elif it.dtype is int:
                    w.setValue(int(it.default))
                elif it.dtype is float:
                    w.setValue(float(it.default))
                else:
                    w.setText(str(it.default))

    def accept(self):
        for it in registry.items():
            w = self._widgets.get((it.section, it.key))
            if w is None:
                continue
            if it.dtype is bool:
                settings.set(it.section, it.key, bool(w.isChecked()))
            elif it.dtype is int:
                settings.set(it.section, it.key, int(w.value()))
            elif it.dtype is float:
                settings.set(it.section, it.key, float(w.value()))
            else:
                settings.set(it.section, it.key, str(w.text()))
        super(PreferencesDialog, self).accept()


def open_preferences():
    dlg = PreferencesDialog()
    (getattr(dlg, 'exec', None) or getattr(dlg, 'exec_', None))()


