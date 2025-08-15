try:
    APP = "houdini"
    import hou

    from utils.qt_compat_layer import QtCore, QtGui
except Exception as e:
    raise

standalone_panels = []

# this will block other ui thread
def showUI(func, *args):
    """
    Show UI instance
    """
    app = QtGui.QApplication.instance()

    if not app:
        app = QtGui.QApplication([APP])

    dialog = func(*args)
    dialog.raise_()
    dialog.show()
    # Qt5/Qt6 兼容执行
    (getattr(dialog, 'exec', None) or getattr(dialog, 'exec_', None))()
    return dialog

def showUIStandalone(func, *args):
    """
    Show UI instance
    """
    app = QtGui.QApplication.instance()

    if not app:
        app = QtGui.QApplication([APP])

    dialog = func(*args)
    dialog.raise_()
    dialog.show()
    global standalone_panels
    standalone_panels.append(dialog)
    return dialog

