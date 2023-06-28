try:
    from Dolag import utils as du
    from PySide2.QtGui import QFont
    from PySide2 import QtGui
    from PySide2 import QtCore
    from PySide2 import QtWidgets
    from console import ConsoleContext, ConsoleItems, ConsoleScore
    from Dolag import utils as du
    import hou
except Exception as e:
    raise


class ConsoleWindow(QtWidgets.QDialog):
    """
    Initial main window
    """

    # singleton pattern
    # __metaclass__ = du.Singleton # maybe qtdialog is already a singleton

    def __init__(self, parent=None, hou_event=None):
        super(ConsoleWindow, self).__init__(parent)
        # context for console item's callback
        self.context = ConsoleContext.ConsoleContext()
        # console items
        self.console_items = ConsoleItems.ItemCollect()
        self.item_list = []
        self.initItem()
        # search lineeditor size
        self.search_width = 325
        self.search_height = 80
        # set panel pos
        self.pos = QtGui.QCursor.pos()
        self.hou_event = hou_event
        # notice main process this window should be close
        self.close_flag = False
        self._initUI()

    def setCloseFlag(self, flag):
        self.close_flag = flag

    def _updateCursorPos(self):
        self.pos = QtGui.QCursor.pos()
        x, y = (self.pos.x(), self.pos.y())
        self.pos.setX(x - self.search_width / 2)
        self.pos.setY(y - self.search_height / 2)

    def initItem(self):
        self.item_list = []
        for key in self.console_items.keys():
            item = self.console_items[key]
            if item.important:
                self.item_list.insert(0, item.item_name)
            else:
                self.item_list.append(item.item_name)

    def loadItems(self):
        self.item_list = []
        for key in self.console_items.keys():
            item = self.console_items[key]
            self.item_list.append(item.item_name)

    def reloadItems(self):
        self.console_items.reload()
        self.loadItems()

    def getEventFromHou(self):
        self.close()

    def updateContext(self, event):
        # pity that this window cannot sense the event in editor
        self._updateCursorPos()
        self.context["editor"] = self.hou_event.editor
        self.context["network_node"] = self.hou_event.editor.pwd()
        self.context["selected_nodes"] = hou.selectedNodes()
        self.context["editor_pos"] = self.hou_event.editor.posFromScreen(self.hou_event.mousepos)
        self.context["hit_item"] = self.hou_event.editor.networkItemsInBox(self.hou_event.mousepos, \
                                                                           self.hou_event.mousepos, for_select=False)
        self.context["screen_pos"] = (self.pos.x(), self.pos.y())
        self.context["qt_keys"] = event.key()

    def searchItem(self, search_str):
        self.item_list = []
        score_item_list = []
        for key in self.console_items.keys():
            item = self.console_items[key]
            item_name = item.item_name.upper()
            alias = item.alias
            if isinstance(alias, tuple):
                alias = alias[0].upper()
            else:
                alias = alias.upper()
            search_str = search_str.upper()
            alias_match_str = ConsoleScore.AliasMatchString(search_str, alias,
                                                            (ConsoleScore.SubStringMatchScore,
                                                             ConsoleScore.SubSequenceMatchScore))
            name_match_str = ConsoleScore.ItemNameMatchString(search_str, item_name,
                                                              (ConsoleScore.SubStringMatchScore,
                                                               ConsoleScore.SubSequenceMatchScore))
            captain = ''.join([word[0] for word in item_name.split(' ')])
            captain_match_str = ConsoleScore.CaptainMatchString(search_str, captain,
                                                                (ConsoleScore.SubStringMatchScore,
                                                                 ConsoleScore.SubSequenceMatchScore))
            eval_score = ConsoleScore.EvalSearchStringScore((alias_match_str, name_match_str, captain_match_str))
            score, rank_score = eval_score.eval()
            # the tuple order means the sort order
            # score > rank_score(alias > name > captain) > name length
            score_item_list.append((score, rank_score, -len(item_name), item))

        # sort decreasingly
        # for python2, it sorts default by index
        import sys
        if sys.version_info.major == 2:
            score_item_list.sort()

        # for python3, we have to use itemgetter
        elif sys.version_info.major == 3:
            from operator import itemgetter
            score_item_list.sort(key=itemgetter(0, 1, 2))

        score_item_list.reverse()
        # extract name as a new list
        new_item_list = [item[-1].item_name for item in score_item_list]
        self.item_list = new_item_list
        self.slmRes.setStringList(self.item_list)
        new_index = self.slmRes.index(0, 0)
        self.smRes.setCurrentIndex(new_index, QtCore.QItemSelectionModel.SelectCurrent)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            # will be close in this uievent session of houdini
            self.close_flag = True
            self.close()

        elif event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            index = self.lvRes.currentIndex()
            if index.row() is None:
                self.close()
                return

            # update context
            self.updateContext(event)
            item_name = self.item_list[index.row()]
            self.console_items[item_name].run(self.context)
            # will be close in this uievent session of houdini
            self.close_flag = True
            self.close()

        elif event.key() == QtCore.Qt.Key_Up:
            pre_index = self.lvRes.currentIndex()
            new_row = (pre_index.row() - 1) % len(self.item_list)
            new_index = self.slmRes.index(new_row, 0)
            self.smRes.setCurrentIndex(new_index, QtCore.QItemSelectionModel.SelectCurrent)

        elif event.key() == QtCore.Qt.Key_Down:
            pre_index = self.lvRes.currentIndex()
            new_row = (pre_index.row() + 1) % len(self.item_list)
            new_index = self.slmRes.index(new_row, 0)
            self.smRes.setCurrentIndex(new_index, QtCore.QItemSelectionModel.SelectCurrent)

        # press ctrl+space then move to cursor
        elif event.key() == QtCore.Qt.Key_Control | QtCore.Qt.Key_Space:
            self._updateCursorPos()
            self.move(self.pos)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        self._updateCursorPos()
        self.move(self.pos)

    def show(self):
        super(ConsoleWindow, self).show()

    def _changeText(self):
        text = self.leSearch.text()
        if text is None or text == '':
            return

        self.searchItem(text)

    def _initUI(self):
        fRes = QFont()
        fRes.setPointSize(16)
        fRes.setBold(True)
        fRes.setWeight(65)

        fSearch = QFont()
        fSearch.setPointSize(16)
        fSearch.setBold(True)
        fSearch.setWeight(75)

        self.blvMain = QtWidgets.QVBoxLayout()
        self.blvMain.setSpacing(0)
        self.blhSearch = QtWidgets.QHBoxLayout()
        # list view to display search result
        self.lvRes = QtWidgets.QListView()
        self.lvRes.setViewMode(QtWidgets.QListView.ListMode)
        self.lvRes.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.lvRes.setObjectName(u"lvRes")
        self.lvRes.setAutoScroll(True)
        self.lvRes.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.lvRes.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.lvRes.setFont(fRes)
        self.lvRes.setFixedSize(self.search_width, 350)

        hint = self.lvRes.sizeHint()
        hint.setHeight(-1)

        # list model of list view
        self.slmRes = QtCore.QStringListModel()
        # select first one
        self.slmRes.setStringList(self.item_list)
        self.lvRes.setModel(self.slmRes)
        idx = self.slmRes.index(0, 0)
        # selection model of list view
        self.smRes = self.lvRes.selectionModel()
        self.smRes.select(idx, QtCore.QItemSelectionModel.Select)
        # initial select
        new_index = self.slmRes.index(0, 0)
        self.smRes.setCurrentIndex(new_index, QtCore.QItemSelectionModel.SelectCurrent)

        # line editor
        self.leSearch = QtWidgets.QLineEdit(self)
        self.leSearch.setFixedSize(self.search_width, self.search_height)
        self.leSearch.setFont(fSearch)
        self.leSearch.textChanged.connect(self._changeText)
        self.leSearch.setPlaceholderText("Search everything here!")
        self.leSearch.installEventFilter(self)

        # layout
        self.blhSearch.addWidget(self.leSearch)
        self.blvMain.addLayout(self.blhSearch)
        self.blvMain.addWidget(self.lvRes, 0, QtCore.Qt.AlignHCenter)

        # main window
        self._updateCursorPos()
        self.move(self.pos)
        self.setLayout(self.blvMain)
        # self.setWindowFlags(self.windowFlags()^self.windowFlags())
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setStyleSheet(hou.ui.mainQtWindow().styleSheet())

    def closeEvent(self, event):
        # detach
        # self.setParent(None)
        self.done(0)
