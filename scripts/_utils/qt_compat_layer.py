try:
	from PySide6 import QtCore as _QtCore
	from PySide6 import QtWidgets as _QtWidgets
	from PySide6 import QtGui as _QtGui
	try:
		from PySide6 import QtSvg as _QtSvg
	except Exception:
		_QtSvg = None
	QT_VERSION = 6
except Exception:
	from PySide2 import QtCore as _QtCore
	from PySide2 import QtWidgets as _QtWidgets
	from PySide2 import QtGui as _QtGui
	try:
		from PySide2 import QtSvg as _QtSvg
	except Exception:
		_QtSvg = None
	QT_VERSION = 2

# Expose modules with names matching existing code style
# - Many places alias QtWidgets as QtGui; keep both available:
QtCore = _QtCore
QtWidgets = _QtWidgets
# In project code, `QtGui` refers to widgets; keep that mapping
QtGui = _QtWidgets
# Real QtGui is exposed as QtG for painting/graphics
QtG = _QtGui
QtSvg = _QtSvg


def exec_dialog(dialog):
	"""Exec dialog across Qt5/Qt6.
	Returns dialog result code when available, otherwise 0.
	"""
	fn = getattr(dialog, 'exec', None) or getattr(dialog, 'exec_', None)
	if callable(fn):
		return fn()
	# Fallback
	dialog.show()
	return 0


def qapplication_instance(app_name='houdini'):
	"""Get or create a QApplication instance safely."""
	app = QtWidgets.QApplication.instance()
	if not app:
		app = QtWidgets.QApplication([app_name])
	return app


def clipboard():
	"""Cross-version clipboard accessor."""
	return QtWidgets.QApplication.clipboard()


def set_font_weight(font, weight):
	"""Set QFont weight compatibly across Qt5/Qt6.

	If Qt6 enum is required, map common integer weights to QFont.Weight.
	"""
	try:
		WeightEnum = getattr(QtG.QFont, 'Weight', None)
		if WeightEnum is not None:
			# Qt6 path
			if isinstance(weight, int):
				w = int(weight)
				if w >= 81:
					enum_val = WeightEnum.ExtraBold
				elif w >= 75:
					enum_val = WeightEnum.Bold
				elif w >= 63:
					enum_val = WeightEnum.DemiBold
				elif w >= 57:
					enum_val = WeightEnum.Medium
				elif w >= 50:
					enum_val = WeightEnum.Normal
				elif w >= 25:
					enum_val = WeightEnum.Light
				elif w >= 12:
					enum_val = WeightEnum.ExtraLight
				else:
					enum_val = WeightEnum.Thin
				font.setWeight(enum_val)
			else:
				font.setWeight(weight)
		else:
			# Qt5 path: accepts int
			font.setWeight(weight)
	except Exception:
		try:
			font.setWeight(weight)
		except Exception:
			pass


__all__ = [
	'QT_VERSION',
	'QtCore',
	'QtWidgets',
	'QtGui',
	'QtG',
	'QtSvg',
	'exec_dialog',
	'qapplication_instance',
	'clipboard',
	'set_font_weight',
]


