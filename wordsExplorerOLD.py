import DateBase as db

import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, \
    QStackedLayout, QHBoxLayout, \
    QVBoxLayout, QTableWidget, \
    QTableWidgetItem, QListWidget, \
    QPlainTextEdit, QLineEdit

from PyQt5.QtWidgets import QAbstractItemView, QHeaderView

from PyQt5.QtWidgets import QLCDNumber, QLabel

ROUNDED_STYLE_SHEET1 = """QPushButton {
     background-color: green;
     color: white;
     border-style: outset;
     border-width: 4px;
     border-radius: 15px;
     border-color: blue;
     font: bold 10px;
     min-width: 10em;
     padding: 8px;
 }"""

# types viewing
TVIEWGROUP = 0
TVIEWGROUPS = 3
TVIEWWORD = 1
TVIEWWORDS = 2

HIDEINDEX = True


def createTable(size, headerLabels, widthColumns, lastStretch=True, maximumHeight=None, hideFColumn=False,
                tableWidget=None):
    # size = (400, 300)
    w, h = size
    n = len(headerLabels)
    print("len(headerLabels)", (headerLabels))

    table = QTableWidget(0, n) if tableWidget is None else tableWidget
    table.setColumnCount(n)
    table.setHorizontalHeaderLabels(headerLabels)
    if hideFColumn:
        table.hideColumn(0)
    if maximumHeight:
        table.setMaximumHeight(maximumHeight)
    # table.setMaximumSize(*size)
    # table.setFixedSize(*size)

    table.setMinimumSize(*size)

    for i in range(n):
        w_c = widthColumns[i]
        if w_c is not None:
            table.setColumnWidth(i, w_c if w_c > 1 else w_c * w)
    print(3)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.horizontalHeader().setStretchLastSection(lastStretch)
    table.verticalHeader().hide()
    # table.horizontalHeader().setSectionResizeMode(n - 1, QHeaderView.ResizeToContents)
    # table.verticalHeader()
    return table


class ExplorerWords(QWidget):
    def __init__(self, base):
        super().__init__()
        self.base = base
        self.initUI()

    def initUI(self):
        # self.setStyleSheet(ROUNDED_STYLE_SHEET1)
        self.main_box = QVBoxLayout()
        self.setLayout(self.main_box)
        self._size = (500, 500)
        # self.setGeometry(500, 500, *self._size)
        self.setWindowTitle("Браузер слов")
        self.stackedLayout = QStackedLayout()
        self.groupsWidget = TableGroupsWidget(self.base,
                                              funcVisibleGroup=self.visibleGroup,
                                              funcAddGroup=lambda: print("addGroup"))
        self.wordsWidget = TableWordsWidget(self.base,
                                            funcVisibleWord=self.visibleWord,
                                            funcBack=self.visibleGroups,
                                            funcAddWord=lambda x: print("addWord", x))

        self.wordVWidget = ViewWordWidget(self.base,
                                          funcEditWord=lambda x: print("EditWord " + str(x)),
                                          funcBack=lambda: self.visibleGroup(self.groupID))

        # tw = TableWords(base, groupID=4, typeView=TVIEWGROUP)
        # tw = TableWords(base, wordID=4, typeView=TVIEWWORD)
        # tw = TableMy(base, typeView=TVIEWWORDS)
        tw = TableMy(base, typeView=TVIEWGROUPS)
        tw.updateTable()

        # self.stackedLayout.addWidget(tw)
        self.stackedLayout.addWidget(self.groupsWidget)
        self.stackedLayout.setCurrentIndex(0)
        self.stackedLayout.addWidget(self.wordsWidget)
        self.stackedLayout.addWidget(self.wordVWidget)
        self.main_box.addLayout(self.stackedLayout)

    def visibleGroup(self, groupID):
        self.groupID = groupID
        print("visibleGroup:", groupID)
        self.wordsWidget.fillTable(groupID)
        self.stackedLayout.setCurrentIndex(1)

    def visibleGroups(self):
        self.groupsWidget.fillTable()
        self.stackedLayout.setCurrentIndex(0)

    def visibleWord(self, wordID):
        print("VWord", wordID)
        # self.wordVWidget.funcBack =
        self.wordVWidget.setWord(wordID)
        self.stackedLayout.setCurrentIndex(2)


class TableGroupsWidget(QWidget):
    def __init__(self, base, funcVisibleGroup=None, funcAddGroup=None):
        super().__init__()
        self.base = base
        self.funcVisibleGroup = lambda: funcVisibleGroup(self.IDsGroup[self.table.currentRow()])
        self.funcAddGroup = funcAddGroup
        self.initUI()

    def initUI(self):
        main_box = QVBoxLayout()
        self.table = self.createTable()

        self.table.cellClicked.connect(self.activCell)
        self.table.cellDoubleClicked.connect(self.funcVisibleGroup)

        main_box.addWidget(self.table)
        self.butLayout = butLayout = QHBoxLayout()
        butLayout.addStretch()
        main_box.addLayout(butLayout)

        self.butAdd = butAdd = QPushButton("Добавить")
        butAdd.clicked.connect(self.funcAddGroup)
        butAdd.setMinimumWidth(100)
        butLayout.addWidget(butAdd)

        self.butVisible = butVisible = QPushButton("Просмотр")
        butVisible.clicked.connect(self.funcVisibleGroup)
        butVisible.setMinimumWidth(100)
        butLayout.addWidget(butVisible)

        self.fillTable()
        self.setLayout(main_box)

    def createTable(self):
        size = (400, 300)
        w, h = size
        self.headerLabels = ['Группа', 'Количество пар', 'Языки']
        table = createTable(size, self.headerLabels, [w * 0.25, w * 0.37, None], lastStretch=True)
        return table

    def fillTable(self):
        self.butVisible.setEnabled(False)
        table = self.table
        table.clear()
        groups = self.base.getGroups()
        n = len(groups)
        print("len(groups)", n)
        table.setRowCount(n)
        table.setHorizontalHeaderLabels(self.headerLabels)
        self.IDsGroup = []
        for i_g in range(n):
            group = groups[i_g]
            self.IDsGroup.append(group["ID"])
            # table.insertRow(i_g)
            langs = group['Languages']
            print(f'{group["ID"]}. Группа: {group["Name"]}  Количество слов: {group["CountWords"]} \n Языки: {langs}')
            labels = (group["Name"], str(group["CountWords"]), "; ".join(map(lambda x: x[1], langs)))
            for i_c in range(3):
                item = QTableWidgetItem(labels[i_c])
                table.setItem(i_g, i_c, item)
        return table

    def activCell(self, row, coumn):
        print("activCell:", row, coumn)
        self.butVisible.setEnabled(True)


class TableWordsWidget(QWidget):
    def __init__(self, base, funcVisibleWord=None, funcBack=None, funcAddWord=None):
        super().__init__()
        self.base = base
        # funcVisibleWord = print
        self.funcVisibleWord = lambda: funcVisibleWord(
            self.IDsWords[self.table.item(self.table.currentRow(), 0).text()])
        self.funcBack = funcBack
        self.funcAddWord = lambda: funcAddWord(self.groupID)
        # self.groupID = groupID
        self.initUI()

    def initUI(self):
        main_box = QVBoxLayout()
        main_box.addWidget(QLabel(f"Группа"))

        self.table = self.createTable()
        self.table.cellClicked.connect(self.activCell)
        self.table.cellDoubleClicked.connect(self.funcVisibleWord)
        self.table.setSortingEnabled(False)

        main_box.addWidget(self.table)
        self.butLayout = butLayout = QHBoxLayout()
        main_box.addLayout(butLayout)

        self.butBack = butBack = QPushButton("Назад к группам")
        butBack.clicked.connect(self.funcBack)
        butBack.setMinimumWidth(130)
        butLayout.addWidget(butBack)

        butLayout.addStretch()

        self.butAdd = butAdd = QPushButton("Добавить")
        butAdd.clicked.connect(self.funcAddWord)
        butAdd.setMinimumWidth(100)
        butLayout.addWidget(butAdd)

        self.butVisible = butVisible = QPushButton("Просмотр")
        butVisible.setEnabled(False)
        butVisible.clicked.connect(self.funcVisibleWord)
        butVisible.setMinimumWidth(100)
        butLayout.addWidget(butVisible)

        self.setLayout(main_box)

    def createTable(self):
        size = (400, 300)
        w, h = size
        self.headerLabels = ['Слово', 'Язык', 'Перевод']
        table = createTable(size, self.headerLabels, [w * 0.37, w * 0.25, None], lastStretch=True)
        return table

    def fillTable(self, groupID=None):
        self.butVisible.setEnabled(False)
        self.table.scrollToTop()
        table = self.table
        groupID = self.groupID if groupID is None else groupID
        self.groupID = groupID
        table.clear()
        words = self.base.getWordsOfGroup(groupID)
        langs = self.base.getAllLanguage()
        # преводим к виду (((ид1, слово1, ид_языка1), (ид2, слово2, ид_языка2)),
        # ((ид3, слово3, ид_языка1), (ид4, слово4, ид_языка2)))
        words = list(
            zip(*map(lambda x: map(lambda y: list(y[1]) + [x[0]], sorted(x[1].items())), sorted(words.items()))))
        print("Words", words)
        n = len(words) * 2
        table.setRowCount(0)
        table.setHorizontalHeaderLabels(['Слово', 'Язык', 'Перевод'])
        self.IDsWords = {}
        print("n:", n)
        for i_g in range(n // 2):
            # группа слов однокового перевода
            groupWord = words[i_g]
            i_w = 0
            # print("i_g", i_g)
            for Word in groupWord:
                idWord, word, idLang = Word
                # ii = i_g + (n // 2) * i_w
                # print(ii, "i_g", i_g, (n // 2) * i_w)
                # self.IDsWords.append(idWord)
                table.insertRow(i_g + i_w)

                # print(f'{group["ID"]}. Группа: {group["Name"]}  Количество слов: {group["CountWords"]} \n Языки: {langs}')
                labels = (word, langs[idLang][0], groupWord[(i_w + 1) % len(groupWord)][1])
                self.IDsWords[labels[0]] = idWord
                # print("labels word:", labels)
                for i_c in range(len(labels)):
                    item = QTableWidgetItem(labels[i_c])
                    table.setItem(i_g + i_w, i_c, item)
                i_w += 1
        print(self.IDsWords)
        return table

    def activCell(self, row, coumn):
        print("activCell:", row, coumn)
        self.butVisible.setEnabled(True)


class ViewWordWidget(QWidget):
    def __init__(self, base, funcBack=None, funcEditWord=None):
        super().__init__()
        self.base = base
        self.funcEditWord = funcEditWord
        self.funcBack = funcBack
        # self.groupID = groupID
        self.initUI()

    def initUI(self):
        main_box = QVBoxLayout()
        self.setLayout(main_box)

        main_box.addWidget(QLabel(f"Просмотр слова"))

        self.labelWord = QLabel()
        main_box.addWidget(self.labelWord)

        self.labelLang = QLabel()
        main_box.addWidget(self.labelLang)

        self.textDiscript = QPlainTextEdit()
        self.textDiscript.setMaximumHeight(50)
        main_box.addWidget(self.textDiscript)

        size = (400, 300)
        w, h = size

        # main_box.addWidget(QLabel("Перевод"))
        sizeT = (400, 80)
        self.headerTranslate = ["Перевод", "Язык"]
        self.tableTranslate = createTable(sizeT, self.headerTranslate, [0.6, None])
        main_box.addWidget(self.tableTranslate)
        # self.setWord lambda r, c: print(self.IDsWords[c]) self.table.item(self.table.currentRow(), 0
        # self.IDsWords[self.table.item(self.table.currentRow(), 0).text()]
        self.tableTranslate.cellDoubleClicked.connect(
            lambda r, c: self.setWord(self.IDsWords[self.tableTranslate.item(r, 0).text()]))

        main_box.addWidget(QLabel("Группы"))
        sizeT = (400, 80)
        self.tableGroups = createTable(sizeT, [""], [None], maximumHeight=80)
        self.tableGroups.horizontalHeader().hide()
        main_box.addWidget(self.tableGroups)

        # self.table.cellClicked.connect(self.activCell)
        # self.table.cellDoubleClicked.connect(self.funcVisibleWord)

        self.butLayout = butLayout = QHBoxLayout()
        main_box.addLayout(butLayout)

        self.butBack = QPushButton("Назад")
        self.butBack.clicked.connect(self.funcBack)
        self.butBack.setMinimumWidth(130)
        butLayout.addWidget(self.butBack)

        self.butLayout.addStretch()

        self.butEdit = QPushButton("Изменить")
        self.butEdit.clicked.connect(self.editWord)
        self.butEdit.setMinimumWidth(130)
        butLayout.addWidget(self.butEdit)
        main_box.addStretch()

    def setWord(self, idWord):
        self.wordID = idWord
        print(1)
        Word = self.base.getWord(idWord)
        print(Word)
        idWord, word, lang, translateID, descript = Word
        langID, lang = lang
        self.labelWord.setText("Слово:\t" + word)
        self.labelLang.setText("Язык:\t" + lang)

        self.textDiscript.setPlainText(descript if descript != db.NULL else "Описание:")
        self.textDiscript.setEnabled(False)
        self.tableGroups.setRowCount(0)
        # self.tableGroups.setHorizontalHeaderLabels(["Группа", "Zpsrb"])
        groups = base.getGroupsWord(idWord)
        for i_g in range(len(groups)):
            groupID, group = groups[i_g]
            self.tableGroups.insertRow(i_g)
            labels = (group,)
            for i_c in range(len(labels)):
                item = QTableWidgetItem(labels[i_c])
                self.tableGroups.setItem(i_g, i_c, item)

        self.tableTranslate.setRowCount(0)
        self.tableTranslate.setHorizontalHeaderLabels(self.headerTranslate)
        self.IDsWords = {}
        wordsT = base.getTranslatesWord(idWord)

        for i_g in range(len(wordsT)):
            wordIDT, wordT, langIDT, langT = wordsT[i_g]
            self.IDsWords[wordT] = wordIDT
            self.tableTranslate.insertRow(i_g)
            labels = (wordT, langT)
            for i_c in range(len(labels)):
                item = QTableWidgetItem(labels[i_c])
                self.tableTranslate.setItem(i_g, i_c, item)
                print("label Trans", labels[i_c])

    def editWord(self):
        print("wordID", self.wordID)
        try:
            self.funcEditWord(self.wordID)
        except:
            print(self.wordID)


class EditWordWidget(QWidget):
    def __init__(self, base, funcBack=None):
        super().__init__()
        self.base = base
        self.funcBack = funcBack
        # self.groupID = groupID
        self.initUI()

    def initUI(self):
        main_box = QVBoxLayout()
        self.setLayout(main_box)

        main_box.addWidget(QLabel(f"Редактор слова"))

        self.labelWord = QLineEdit()
        main_box.addWidget(self.labelWord)

        self.labelLang = QLabel()
        main_box.addWidget(self.labelLang)

        self.textDiscript = QPlainTextEdit()
        self.textDiscript.setMaximumHeight(50)
        main_box.addWidget(self.textDiscript)

        size = (400, 300)
        w, h = size

        # main_box.addWidget(QLabel("Перевод"))
        sizeT = (400, 80)
        self.headerTranslate = ["Перевод", "Язык"]
        self.tableTranslate = createTable(sizeT, self.headerTranslate, [0.6, None])
        main_box.addWidget(self.tableTranslate)
        # self.setWord lambda r, c: print(self.IDsWords[c]) self.table.item(self.table.currentRow(), 0
        # self.IDsWords[self.table.item(self.table.currentRow(), 0).text()]
        self.tableTranslate.cellDoubleClicked.connect(
            lambda r, c: self.setWord(self.IDsWords[self.tableTranslate.item(r, 0).text()]))

        main_box.addWidget(QLabel("Группы"))
        sizeT = (400, 80)
        self.tableGroups = createTable(sizeT, [""], [None], maximumHeight=80)
        self.tableGroups.horizontalHeader().hide()
        main_box.addWidget(self.tableGroups)

        # self.table.cellClicked.connect(self.activCell)
        # self.table.cellDoubleClicked.connect(self.funcVisibleWord)

        self.butLayout = butLayout = QHBoxLayout()
        main_box.addLayout(butLayout)

        self.butBack = QPushButton("Назад")
        self.butBack.clicked.connect(self.funcBack)
        self.butBack.setMinimumWidth(130)
        butLayout.addWidget(self.butBack)

        self.butLayout.addStretch()

        self.butEdit = QPushButton("Изменить")
        self.butEdit.clicked.connect(self.editWord)
        self.butEdit.setMinimumWidth(130)
        butLayout.addWidget(self.butEdit)
        main_box.addStretch()

    def setWord(self, groupID=None):
        self.wordID = idWord
        print(1)
        Word = self.base.getWord(idWord)
        print(Word)
        idWord, word, lang, translateID, descript = Word
        langID, lang = lang
        self.labelWord.setText("Слово:\t" + word)
        self.labelLang.setText("Язык:\t" + lang)

        self.textDiscript.setPlainText(descript if descript != db.NULL else "Описание:")

        self.tableGroups.setRowCount(0)
        # self.tableGroups.setHorizontalHeaderLabels(["Группа", "Zpsrb"])
        groups = base.getGroupsWord(idWord)
        for i_g in range(len(groups)):
            groupID, group = groups[i_g]
            self.tableGroups.insertRow(i_g)
            labels = (group,)
            for i_c in range(len(labels)):
                item = QTableWidgetItem(labels[i_c])
                self.tableGroups.setItem(i_g, i_c, item)

        self.tableTranslate.setRowCount(0)
        self.tableTranslate.setHorizontalHeaderLabels(self.headerTranslate)
        self.IDsWords = {}
        wordsT = base.getTranslatesWord(idWord)

        for i_g in range(len(wordsT)):
            wordIDT, wordT, langIDT, langT = wordsT[i_g]
            self.IDsWords[wordT] = wordIDT
            self.tableTranslate.insertRow(i_g)
            labels = (wordT, langT)
            for i_c in range(len(labels)):
                item = QTableWidgetItem(labels[i_c])
                self.tableTranslate.setItem(i_g, i_c, item)
                print("label Trans", labels[i_c])

    def editWord(self):
        print("wordID", self.wordID)
        try:
            self.funcEditWord(self.wordID)
        except:
            print(self.wordID)


class TableMy(QTableWidget):
    def __init__(self, base, size=(500, 300), maxHeight=None, wordID=True, groupID=None,
                 typeView=TVIEWGROUP, cellClicked=None, cellDoubleClicked=None):
        super().__init__()
        self.base = base
        self.typeView = typeView
        self._size = size
        headerLabels = ["ID"]
        widthColumns = [0]
        if typeView == TVIEWWORD:
            self.wordID = wordID
            headerLabels += ["Слово", "Язык"]
            widthColumns += [0.5, None]
        elif typeView == TVIEWGROUP:
            self.groupID = groupID
            headerLabels += ["Слово", "Язык", "Перевод"]
            widthColumns += [0.45, 0.23, None]
        elif typeView == TVIEWWORDS:
            headerLabels += ["Слово", "Язык", "Описание"]
            widthColumns += [0.35, 0.23, None]
        elif typeView == TVIEWGROUPS:
            headerLabels += ['Группа', 'Количество пар', 'Языки']
            widthColumns += [0.35, 0.23, None]

        self.headerLabels = headerLabels
        print("size, headerLabels, widthColumns", size, headerLabels, widthColumns)
        createTable(size, headerLabels, widthColumns, lastStretch=True, maximumHeight=maxHeight, hideFColumn=HIDEINDEX,
                    tableWidget=self)
        self.setCellClicked(cellClicked)
        self.setCellDoubleClicked(cellDoubleClicked)
        print(1)

    def setCellClicked(self, func):
        if func:
            self.cellClicked.connect(lambda r, c: func(self.item(r, 0).text()))

    def setCellDoubleClicked(self, func):
        if func:
            self.cellDoubleClicked.connect(lambda r, c: func(self.item(r, 0).text()))

    def updateTable(self):
        self.clear()
        self.setRowCount(0)
        self.setHorizontalHeaderLabels(self.headerLabels)
        if self.typeView == TVIEWGROUP:
            wordsTR = self.base.getWordsOfGroupSTR(self.groupID)
            # [('74', 'plate', 'Английский', 'тарелка'), ...]
            rows = [(str(ws[i][0]), ws[i][1], ws[i][3], ws[-(i + 1)][1]) for grID, ws in wordsTR.items() for i in
                     range(2)]
        if self.typeView == TVIEWGROUPS:
            groups = self.base.getGroups()
            # [('74', 'plate', 'Английский', 'тарелка'), ...]
            rows = [(str(group["ID"]), group["Name"], str(group["CountWords"]),
                       "; ".join(map(lambda x: x[1], group["Languages"]))) for group in groups]

        elif self.typeView == TVIEWWORD:
            wordsTR = base.getTranslatesWord(self.wordID)
            # [('74', 'plate', 'Английский'), ...]
            rows = [(str(w[0]), w[1], w[3]) for w in wordsTR]
        elif self.typeView == TVIEWWORDS:
            wordsTR = base.getAllWords()
            # [('74', 'plate', 'Английский', 'описание'), ...]
            rows = [(str(w[0]), w[1], w[3], w[5]) for w in wordsTR]
        print("rows", rows)
        n = len(rows)
        print("n:", n)

        for i in range(n):
            self.insertRow(i)
            aRow = rows[i]
            print(aRow)
            for j in range(len(aRow)):
                item = QTableWidgetItem(aRow[j])
                self.setItem(i, j, item)

        return self


if __name__ == '__main__':
    app = QApplication(sys.argv)
    base = db.DateBase("Learning_translate.sqlite")
    window = ExplorerWords(base)
    window.show()
    sys.exit(app.exec())