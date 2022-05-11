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


class ImportWindow(QtGui.QDialog):
    """
    Initial main window
    """
    def __init__(self, func_dict=None, snippet_type=SnippetType.vex, parent=None):
        """
        """
        super(ImportWindow, self).__init__(parent)
        if func_dict is None:
            func_dict = dict()
        self.text = None
        self.snippet_type = SnippetType.vex
        if SnippetType.end > snippet_type >= 0:
            self.snippet_type = snippet_type

        self.comment = None
        self.snippet = None
        self.vex_type = VexType.h
        self.func_dict = {}
        self.func_list = []
        if func_dict:
            self.func_dict = func_dict
            # get func list
            for key in func_dict.keys():
                for func_name in func_dict[key]:
                    func_str = key.split('\\')[-1] + " -> " + func_name
                    self.func_list.append(func_str)

            self.func_list = list(set(self.func_list))
            self.func_list.sort()

        self.slmFunc = QtCore.QStringListModel()
        self.slmFunc.setStringList(self.func_list)
        self._initUI()

    def getSnippet(self):
        return self.snippet

    def getComment(self):
        return self.comment

    def getVexType(self):
        return int(self.vex_type)

    def __onPressImport(self):
        index = self.lvFunc.currentIndex().row()
        file_name = self.func_list[index].split(' -> ')[0]
        file_path = None
        for key in self.func_dict.keys():
            if file_name in key:
                file_path = key

        if file_path is None:
            displayError("Error: Wrong file name")
            return

        if self.snippet_type == SnippetType.vex:
            self.snippet = "#include <{0}>\n".format(file_name)

        elif self.snippet_type == SnippetType.python:
            # strip ".py"
            self.snippet = "import {0}\n".format(file_name[:-3])

        else:
            displayError("Error: Wrong snippet type")
            return

        self.close()

    def __onPressCancel(self):
        # if press cancel
        self.close()

    def _initUI(self):
        blvMain = QtGui.QVBoxLayout()
        blvMain.setObjectName(u"blvMain")
        blvMain.setContentsMargins(0, 0, 0, 0)

        # set list view model
        self.lvFunc = QtGui.QListView()
        self.lvFunc.setViewMode(QtGui.QListView.ListMode)
        self.lvFunc.setObjectName(u"lvFunc")
        # bind model
        self.lvFunc.setModel(self.slmFunc)
        self.lvFunc.setProperty("isWrapping", False)
        self.lvFunc.setUniformItemSizes(False)
        self.lvFunc.setSelectionRectVisible(False)

        blvMain.addWidget(self.lvFunc)
        self.blhButtons = QtGui.QHBoxLayout()
        self.blhButtons.setObjectName(u"blhButtons")
        self.pbImport = QtGui.QPushButton("Import")
        self.pbImport.clicked.connect(self.__onPressImport)
        self.pbCancel = QtGui.QPushButton("Cancel")
        self.pbCancel.clicked.connect(self.__onPressCancel)

        self.blhButtons.addWidget(self.pbImport)
        self.blhButtons.addWidget(self.pbCancel)

        blvMain.addLayout(self.blhButtons)

        # window setting
        if self.snippet_type == SnippetType.python:
            self.setWindowTitle("Import Python Snippet")

        elif self.snippet_type == SnippetType.vex:
            self.setWindowTitle("Import Vex Snippet")

        self.setLayout(blvMain)
        self.resize(QtCore.QSize(350, 450))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def closeEvent(self, event):
        self.done(0)
