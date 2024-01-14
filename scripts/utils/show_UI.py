try:
    APP = "houdini"
    import hou

    from PySide2 import QtCore
    from PySide2 import QtWidgets as QtGui
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
    dialog.exec_()
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

