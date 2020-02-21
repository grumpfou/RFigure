from PyQt5 import QtGui, QtCore, QtWidgets

# add a simple function to the QCheckBox that return the checked state of the CheckBox
def isChecked_WW(self):
    # assert not self.isTristate
    assert not self.isTristate()
    if self.checkState () == QtCore.Qt.Checked:
        return True
    else :
        return False
QtWidgets.QCheckBox.isChecked=isChecked_WW


class FindReplaceDialog(QtWidgets.QDialog):
    def __init__(self,textedit,*args,**kargs):
        """
        This function will display a window to find for partern in the textedit file.
        textedit : QtWidgets.QTextEdit
            the QTextEdit instance in which we have to find
        """
        QtWidgets.QDialog.__init__(self,parent=textedit,*args,**kargs)
        self.setWindowTitle('Find and replace')
        self.textedit = textedit

        self.find_line        = QtWidgets.QLineEdit ()
        self.replace_line    = QtWidgets.QLineEdit ()

        # Options check boxes:
        self.casse_checkbox = QtWidgets.QCheckBox()
        self.regexp_checkbox = QtWidgets.QCheckBox()
        self.entireword_checkbox = QtWidgets.QCheckBox()

        find_button = QtWidgets.QPushButton("&Find")
        replace_button = QtWidgets.QPushButton("&Replace")
        replaceall_button = QtWidgets.QPushButton("&Replace All")
        # find_button.setIcon(QtGui.QIcon(os.path.join(abs_path_icon,"find.png")))

        main_layout=QtWidgets.QFormLayout()
        main_layout.addRow(self.find_line,find_button)
        main_layout.addRow(self.replace_line ,replace_button)
        main_layout.addRow(None ,replaceall_button)
        main_layout.addRow("Casse sensitive",self.casse_checkbox)
        main_layout.addRow("Regular expression",self.regexp_checkbox)
        main_layout.addRow("Entire word",self.entireword_checkbox)

        self. setLayout ( main_layout )

        # Connections:
        find_button.clicked.connect( lambda :self.SLOT_find())
        # self.find_line.returnPressed  .connect( lambda :self.SLOT_find())
        replace_button.clicked.connect( lambda :self.SLOT_replace())
        replaceall_button.clicked.connect( lambda :self.SLOT_replaceall())



    def SLOT_find(self,cursor=None,loop=True,reverse=False,clearselection=False):
        """
        cursor : QtGui.QTextCursor
            the cursor at which the search begins
        loop : bool
            if True will loop the search when reaching the end of the document
            (or the begining of the document when `reverse==True`)
        reverse : bool
            if True, the search goes backwards
        clearselection : bool
            if True, clear the selection of the cursor before beginging
            (it allows to stay in place if the cursor already selected the
            pattern)
        """

        pattern=str(self.find_line.text())
        regexp = self.regexp_checkbox.isChecked()
        if pattern=="":
            return False
        if  regexp :
            pattern = QtCore.QRegExp(pattern)

        flags = 0
        if self.entireword_checkbox.isChecked():
            flags = flags|QtGui.QTextDocument.FindWholeWords
        if self.entireword_checkbox.isChecked():
            flags = flags|QtGui.QTextDocument.FindCaseSensitively
        if reverse:
            flags = flags|QtGui.QTextDocument.FindBackward

        if cursor is None:
            cursor = self.textedit.textCursor()
        if clearselection :
            cursor.setPosition(cursor.selectionEnd() if reverse else  cursor.selectionStart())
        elif cursor.hasSelection():
            # this is necessary if we search `'aba'` in the string `'abababababa'`
            cursor.setPosition(cursor.selectionStart() if reverse else  cursor.selectionStart()+1)

            # if (regexp and pattern.exactMatch(cursor.selectedText())) or (cursor.selectedText()==pattern):
            #     cur.movePosition(QtGui.QTextCursor.Right if reverse else QtGui.QTextCursor.Left,QtGui.QTextCursor.MoveAnchor)

        cursor = self.textedit.document().find(pattern,cursor,QtGui.QTextDocument.FindFlags(flags))
        if not cursor.isNull():
            self.textedit.setTextCursor (cursor)
            return cursor
        elif loop:
            cursor = QtGui.QTextCursor(self.textedit.document())
            if reverse:
                cursor.movePosition(QtGui.QTextCursor.End)
            return self.SLOT_find(cursor=cursor,loop=False,reverse=reverse,
                                                clearselection=clearselection)
        return False


    def SLOT_replace(self,cursor = None,*args,**kargs):
        next_text = str(self.replace_line.text())
        cursor = self.SLOT_find(*args,**kargs,clearselection=True)
        if cursor:
            cursor.insertText(next_text)
        return self.SLOT_find(*args,**kargs)


    def SLOT_replaceall(self,*args,**kargs):
        cursor = self.SLOT_replace(*args,**kargs)
        while cursor:
            cursor = self.SLOT_replace(*args,**kargs)
