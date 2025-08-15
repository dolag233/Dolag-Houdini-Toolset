try:
    APP = "houdini"
    import hou
    from utils.check_filename import checkInvalidFileName
    from error.error_report import displayError
    from utils.code_type import SnippetType, VexType
    from utils.qt_compat_layer import QtCore, QtGui
except Exception as e:
    raise


class AliasWindow(QtGui.QDialog):
    """
    Initial main window
    """
    def __init__(self, parent=None):
        super(AliasWindow, self).__init__(parent)
        self.alias = None
        self._initUI()

    def getAlias(self):
        return self.alias

    def __onPressSave(self):
        # check snippet type
        self.alias = self.leAlias.text()
        self.close()

    def __onPressCancel(self):
        # if press cancel
        self.close()

    def _initUI(self):
        blvMain = QtGui.QVBoxLayout()
        blhAlias = QtGui.QHBoxLayout()
        blhButtons = QtGui.QHBoxLayout()
        self.leAlias = QtGui.QLineEdit(self)
        self.lbAlias = QtGui.QLabel("Alias")
        self.pbSave = QtGui.QPushButton("Save")
        self.pbSave.setFixedWidth(100)
        self.pbSave.clicked.connect(self.__onPressSave)
        self.pbCancel = QtGui.QPushButton("Cancel")
        self.pbCancel.setFixedWidth(100)
        self.pbCancel.clicked.connect(self.__onPressCancel)

        blhAlias.addWidget(self.lbAlias)
        blhAlias.addWidget(self.leAlias)
        blhButtons.addWidget(self.pbSave, 0, QtCore.Qt.AlignRight)
        blhButtons.addWidget(self.pbCancel, 0, QtCore.Qt.AlignRight)
        blvMain.addLayout(blhAlias)
        blvMain.addLayout(blhButtons)

        self.setLayout(blvMain)
        self.resize(QtCore.QSize(400, 150))
        self.setWindowTitle("Create otl alias")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def closeEvent(self, event):
        self.done(0)
