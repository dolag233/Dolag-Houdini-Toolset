try:
    APP = "houdini"
    import hou
    from _utils.check_filename import checkInvalidFileName
    from error.error_report import displayError
    from _utils.code_type import SnippetType, VexType
    from _utils.qt_compat_layer import QtCore, QtGui
    from .pip_install import pipInstall, pipUninstall, pipUpgrade
except Exception as e:
    raise

class PipWindow(QtGui.QDialog):
    """
    Initial main window
    """
    def __init__(self, parent=None):
        super(PipWindow, self).__init__(parent)
        self.module_name = ""
        self.version = ""
        self._initUI()

    def __onPressInstall(self):
        self.module_name = self.leModule.text()
        self.version = self.leVersion.text()
        if self.module_name == "" or self.module_name is None:
            displayError("Empty module name!")
            return

        pipInstall(self.module_name, self.version)

    def __onPressUninstall(self):
        self.module_name = self.leModule.text()
        self.version = self.leVersion.text()
        if self.module_name == "" or self.module_name is None:
            displayError("Empty module name!")
            return

        pipUninstall(self.module_name)

    def __onPressUpgrade(self):
        self.module_name = self.leModule.text()
        self.version = self.leVersion.text()
        if self.module_name == "" or self.module_name is None:
            displayError("Empty module name!")
            return

        pipUpgrade(self.module_name)

    def __onPressCancel(self):
        # if press cancel
        self.close()

    def _initUI(self):
        blvMain = QtGui.QVBoxLayout()
        blhAlias = QtGui.QHBoxLayout()
        blhButtons = QtGui.QHBoxLayout()
        self.leModule = QtGui.QLineEdit(self)
        self.lbModule = QtGui.QLabel("Module")
        self.leVersion = QtGui.QLineEdit(self)
        self.lbVersion = QtGui.QLabel("version")
        self.pbInstall = QtGui.QPushButton("Install")
        self.pbInstall.setFixedWidth(100)
        self.pbInstall.clicked.connect(self.__onPressInstall)
        self.pbUninstall = QtGui.QPushButton("Uninstall")
        self.pbUninstall.setFixedWidth(100)
        self.pbUninstall.clicked.connect(self.__onPressUninstall)
        self.pbUpgrade = QtGui.QPushButton("Upgrade")
        self.pbUpgrade.setFixedWidth(100)
        self.pbUpgrade.clicked.connect(self.__onPressUpgrade)
        self.pbCancel = QtGui.QPushButton("Cancel")
        self.pbCancel.setFixedWidth(100)
        self.pbCancel.clicked.connect(self.__onPressCancel)

        blhAlias.addWidget(self.lbModule)
        blhAlias.addWidget(self.leModule)
        blhAlias.addWidget(self.lbVersion)
        blhAlias.addWidget(self.leVersion)
        blhButtons.addWidget(self.pbInstall, 0, QtCore.Qt.AlignRight)
        blhButtons.addWidget(self.pbUninstall, 0, QtCore.Qt.AlignRight)
        blhButtons.addWidget(self.pbUpgrade, 0, QtCore.Qt.AlignRight)
        blhButtons.addWidget(self.pbCancel, 0, QtCore.Qt.AlignRight)
        blvMain.addLayout(blhAlias)
        blvMain.addLayout(blhButtons)

        self.setLayout(blvMain)
        self.resize(QtCore.QSize(400, 150))
        self.setWindowTitle("Pip Install")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint)

    def closeEvent(self, event):
        self.done(0)
