try:
    APP = "houdini"
    import hou
    from utils.check_filename import checkInvalidFileName
    from error.error_report import displayError
    from utils.code_type import SnippetType, VexType
    from PySide2 import QtCore
    from PySide2 import QtWidgets as QtGui
except Exception as e:
    raise


class SaveWindow(QtGui.QDialog):
    """
    Initial main window
    """
    def __init__(self, snippet_type=SnippetType.vex, parent=None):
        """
        """
        super(SaveWindow, self).__init__(parent)
        self.text = None
        self.snippet_type = SnippetType.vex
        if SnippetType.end > snippet_type >= 0:
            self.snippet_type = snippet_type

        self.comment = None
        self.vex_type = VexType.h
        self._initUI()

    def getText(self):
        return self.text

    def getComment(self):
        return self.comment

    def getVexType(self):
        if hasattr(self.vex_type, "value"):
            return self.vex_type.value

        return int(self.vex_type)

    def __onPressSave(self):
        # check snippet type
        if self.snippet_type == SnippetType.vex:
            # vex header type
            if self.rbVfl.isChecked():
                self.vex_type = VexType.vfl
            elif self.rbHeader.isChecked():
                self.vex_type = VexType.h
            else:
                return

        # if file name is not legal
        if not checkInvalidFileName(self.leFile.text()):
            displayError("filename")
            return

        self.text = self.leFile.text()
        self.comment = self.leComment.text()
        self.close()

    def __onPressCancel(self):
        # if press cancel
        self.close()

    def _initUI(self):
        if self.snippet_type == SnippetType.python:
            blvMain = QtGui.QVBoxLayout()
            blhButtons = QtGui.QHBoxLayout()
            blhComment = QtGui.QHBoxLayout()
            blhMain = QtGui.QHBoxLayout()
            self.leFile = QtGui.QLineEdit(self)
            self.lbFile = QtGui.QLabel("File Name")
            self.lbComment = QtGui.QLabel("Comment")
            self.leComment = QtGui.QLineEdit(self)
            self.pbSave = QtGui.QPushButton("Save")
            self.pbSave.setFixedWidth(100)
            self.pbSave.clicked.connect(self.__onPressSave)
            self.pbCancel = QtGui.QPushButton("Cancel")
            self.pbCancel.setFixedWidth(100)
            self.pbCancel.clicked.connect(self.__onPressCancel)

            blhMain.addWidget(self.lbFile)
            blhMain.addWidget(self.leFile)
            blhButtons.addWidget(self.pbSave, 0, QtCore.Qt.AlignRight)
            blhButtons.addWidget(self.pbCancel, 0, QtCore.Qt.AlignRight)
            blhComment.addWidget(self.lbComment)
            blhComment.addWidget(self.leComment)
            blhMain.layoutSpacing = 2
            blvMain.addLayout(blhMain)
            blvMain.addLayout(blhComment)
            blvMain.addLayout(blhButtons)
            blhMain.layoutSpacing = 5

            self.setLayout(blvMain)
            self.resize(QtCore.QSize(400, 150))
            self.setWindowTitle("Save Vex/Python Snippet")
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        elif self.snippet_type == SnippetType.vex:
            blvMain = QtGui.QVBoxLayout()
            blhButtons = QtGui.QHBoxLayout()
            blhRadios = QtGui.QHBoxLayout()
            blhComment = QtGui.QHBoxLayout()
            blhMain = QtGui.QHBoxLayout()
            self.leFile = QtGui.QLineEdit(self)
            self.lbFile = QtGui.QLabel("File Name")
            self.lbVexType = QtGui.QLabel("Save as")
            self.rbVfl = QtGui.QRadioButton(".vfl")
            # set default select
            self.rbVfl.checked = True
            self.rbHeader = QtGui.QRadioButton(".h")
            self.lbComment = QtGui.QLabel("Comment")
            self.leComment = QtGui.QLineEdit(self)
            self.pbSave = QtGui.QPushButton("Save")
            self.pbSave.setFixedWidth(100)
            self.pbSave.clicked.connect(self.__onPressSave)
            self.pbCancel = QtGui.QPushButton("Cancel")
            self.pbCancel.setFixedWidth(100)
            self.pbCancel.clicked.connect(self.__onPressCancel)

            blhMain.addWidget(self.lbFile)
            blhMain.addWidget(self.leFile)
            blhButtons.addWidget(self.pbSave, 0, QtCore.Qt.AlignRight)
            blhButtons.addWidget(self.pbCancel, 0, QtCore.Qt.AlignRight)
            blhComment.addWidget(self.lbComment)
            blhComment.addWidget(self.leComment)
            blhRadios.addWidget(self.rbVfl, 0, QtCore.Qt.AlignRight)
            blhRadios.addWidget(self.rbHeader, 0, QtCore.Qt.AlignRight)
            blhMain.layoutSpacing = 2
            blvMain.addLayout(blhMain)
            blvMain.addLayout(blhComment)
            blvMain.addLayout(blhRadios)
            blvMain.addLayout(blhButtons)
            blhMain.layoutSpacing = 5

        else:
            return

        self.setLayout(blvMain)
        self.resize(QtCore.QSize(400, 150))
        self.setWindowTitle("Save Vex/Python Snippet")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def closeEvent(self, event):
        self.done(0)
