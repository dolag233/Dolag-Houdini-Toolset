try:
    APP = "houdini"
    import hou

    from PySide2 import QtCore
    from PySide2 import QtWidgets as QtGui
except Exception as e:
    raise


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