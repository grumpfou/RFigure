# PYTHON 3
from PyQt5 import QtGui,QtCore,QtWidgets
from .findReplace import FindReplaceDialog

import sys
if __name__=='__main__':
    import syntax
else:
    from . import syntax

FONT = {
    'size':10,
    'name':'DejaVu Sans Mono',
    'indent':4,
    }


def selectBlocks(self):
    i0 = self.selectionStart()
    i1 = self.selectionEnd()

    self.setPosition(self.document().findBlock(i0).position(),QtGui.QTextCursor.MoveAnchor)
    self.movePosition(QtGui.QTextCursor.Left,QtGui.QTextCursor.MoveAnchor)
    self.setPosition(i1,QtGui.QTextCursor.KeepAnchor)
    self.movePosition(QtGui.QTextCursor.EndOfBlock,QtGui.QTextCursor.KeepAnchor)
QtGui.QTextCursor.selectBlocks = selectBlocks



def yieldBlockInSelection_WW(self,direction=1):
    """
    - direction : if positive, then will go forward otherwise, it will go
            backward.
    """
    pos1=self.selectionStart()
    pos2=self.selectionEnd ()

    startCursor=QtGui.QTextCursor(self)
    endCursor=QtGui.QTextCursor(self)
    startCursor.setPosition(pos1)
    endCursor  .setPosition(pos2)

    if direction>=0:
        bl=startCursor.block()
        bl_end=endCursor.block()
    else:
        bl=endCursor.block()
        bl_end=startCursor.block()

    yield bl
    while bl!=bl_end:
        if direction>=0:bl=bl.next()
        # if direction>=0:bl=bl.previous()
        else:bl=bl.previous()
        yield bl
QtGui.QTextCursor.yieldBlockInSelection=yieldBlockInSelection_WW


class RLineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
        QtWidgets.QWidget.__init__(self,editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QtCore.QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)



class RPythonEditor(QtWidgets.QPlainTextEdit):
    delimiters = {
                    "'":"''",
                    '"':'""',
                    '(':'()',
                    '[':'[]',
                    '{':'{}',
                    }
    def __init__(self,parent=None):
        QtWidgets.QPlainTextEdit.__init__(self,parent=parent)
        self.highlight = syntax.PythonHighlighter(self.document())

        # set monospace font
        font = self.document().defaultFont()
        font.setFamily(FONT['name'])
        font.setPointSize(FONT['size'])
        self.document().setDefaultFont(font)

        # indent :
        fm = QtGui.QFontMetrics(font)
        indent_size = fm.tightBoundingRect(" "*(FONT['indent']+1)).width()-1
        self.setTabStopWidth(indent_size)

        # no wrap
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

        self.lineNumberArea = RLineNumberArea(self)

        self.setup_connections()

        self.updateLineNumberAreaWidth(0)
        self.findDialog =  FindReplaceDialog(textedit=self)

    def setup_connections(self):
        # actions
        self.actionCommentDecomment    = QtWidgets.QAction("Comment/Decomment",self)
        self.actionDeleteLine    = QtWidgets.QAction("Delete Line",self)
        self.actionDuplicateLine    = QtWidgets.QAction("Duplicate Line",self)
        self.actionMoveLineUp    = QtWidgets.QAction("Move Line Up",self)
        self.actionMoveLineDown    = QtWidgets.QAction("Move Line Down",self)
        self.actionReshapeOneLine    = QtWidgets.QAction("Reshape in one line",self)
        self.actionLaunchFindDialog    = QtWidgets.QAction("Open the search dialog",self)
        self.actionFindNext    = QtWidgets.QAction("Search Next",self)
        self.actionFindPrevious    = QtWidgets.QAction("Search Previous",self)

        self.addAction(self.actionCommentDecomment)
        self.addAction(self.actionDeleteLine)
        self.addAction(self.actionDuplicateLine)
        self.addAction(self.actionMoveLineUp)
        self.addAction(self.actionMoveLineDown)
        self.addAction(self.actionReshapeOneLine)
        self.addAction(self.actionLaunchFindDialog)
        self.addAction(self.actionFindNext)
        self.addAction(self.actionFindPrevious)

        self.actionCommentDecomment.setShortcuts(QtGui.QKeySequence("Ctrl+/"))
        self.actionDeleteLine.setShortcuts(QtGui.QKeySequence("Ctrl+Shift+K"))
        self.actionDuplicateLine.setShortcuts(QtGui.QKeySequence("Ctrl+Shift+D"))
        self.actionMoveLineUp.setShortcuts(QtGui.QKeySequence("Ctrl+Up"))
        self.actionMoveLineDown.setShortcuts(QtGui.QKeySequence("Ctrl+Down"))
        self.actionReshapeOneLine.setShortcuts(QtGui.QKeySequence("Ctrl+J"))
        self.actionLaunchFindDialog.setShortcuts(QtGui.QKeySequence("Ctrl+F"))
        self.actionFindNext.setShortcuts(QtGui.QKeySequence.FindNext)
        self.actionFindPrevious.setShortcuts(QtGui.QKeySequence.FindPrevious)

        self.actionCommentDecomment .triggered.connect(self.SLOT_actionCommentDecomment)
        self.actionDeleteLine       .triggered.connect(self.SLOT_actionDeleteLine)
        self.actionDuplicateLine    .triggered.connect(self.SLOT_actionDuplicateLine)
        self.actionMoveLineUp       .triggered.connect(self.SLOT_actionMoveLineUp)
        self.actionMoveLineDown     .triggered.connect(self.SLOT_actionMoveLineDown)
        self.actionReshapeOneLine   .triggered.connect(self.SLOT_actionReshapeOneLine)
        self.actionLaunchFindDialog .triggered.connect(self.SLOT_actionLaunchFindDialog)
        self.actionFindNext         .triggered.connect(lambda : self.findDialog.SLOT_find(loop=True))
        self.actionFindPrevious     .triggered.connect(lambda : self.findDialog.SLOT_find(loop=True,reverse=True))

        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)


    def keyPressEvent(self,e):
        cur = self.textCursor()
        if cur.hasSelection() and (e.key() == QtCore.Qt.Key_Tab):
            # cur.selectBlocks()
            for bl in cur.yieldBlockInSelection():
                cur1 = QtGui.QTextCursor(bl)
                cur1.insertText('\t')
        elif e.key() == QtCore.Qt.Key_Backtab:
            for bl in cur.yieldBlockInSelection():
                cur1 = QtGui.QTextCursor(bl)
                cur1.movePosition(QtGui.QTextCursor.Right,QtGui.QTextCursor.KeepAnchor)
                if str(cur1.selectedText())=='\t':
                    cur1.removeSelectedText()

        # increase the indentation corresponding to the previous line
        elif  e.key() in [QtCore.Qt.Key_Enter,QtCore.Qt.Key_Return]:
            QtWidgets.QPlainTextEdit.keyPressEvent(self,e)

            cur = self.textCursor()
            cur.select(QtGui.QTextCursor.BlockUnderCursor)
            if str(cur.selectedText()).strip()=="":# if it is an empty line
                prev_text = cur.block().previous().text()
                i = 0
                while i<len(prev_text) and prev_text[i]=='\t' : i+=1
                prev_text = prev_text.split('#')[0].strip()
                if len(prev_text)>0 and prev_text[-1]==':': i+=1
                cur.insertText('\t'*i)

        elif e.text() in self.delimiters:
            # QtWidgets.QTextEdit.keyPressEvent(self,event)
            self.blockSignals(True)
            cursor=self.insert_delimiters(e.text(),self.textCursor())
            # cursor = self.language.check_delimiters()
            self.setTextCursor(cursor)
            self.blockSignals(False)

        else:
            QtWidgets.QPlainTextEdit.keyPressEvent(self,e)

    def setPlainText(self,text):
        text = text.replace('    ','\t')# we replace the spaces by tabs
        QtWidgets.QPlainTextEdit.setPlainText(self,text)

    def insertFromMimeData(self,source ):
        """A re-implementation of insertFromMimeData. We have to check the
        typography of what we have just paste.
        TODO : some summary window of all the corrections.
        """
        text=str(source.text())
        text = text.replace('    ','\t')
        cursor=self.textCursor()
        cursor.insertText(text)

    @QtCore.pyqtSlot()
    def SLOT_actionCommentDecomment(self):
        cur1 = self.textCursor()
        cur1.beginEditBlock()

        for current_block in cur1.yieldBlockInSelection():
            # current_block = cur.block()
            if not len((str(current_block.text())).strip())==0:
                #if it is an empty line: do nothing

                cur = QtGui.QTextCursor( current_block )
                cur.movePosition(QtGui.QTextCursor.StartOfBlock)

                # i = current_block.position()
                # end_pos = current_block.position()+current_block.length()
                charAt = lambda x: str(self.document().characterAt(x))
                while (not cur.atBlockEnd()) and charAt(cur.position()) in [' ','\t']:
                    cur.movePosition(QtGui.QTextCursor.NextCharacter)
                c = charAt(cur.position())
                if c != '#':
                    cur.insertText('# ')
                else:
                    cur.deleteChar()
                    while charAt(cur.position())==' ':
                        cur.deleteChar()
        cur1.endEditBlock()

    def SLOT_actionDeleteLine(self):
        cur = self.textCursor()
        cur.beginEditBlock()
        cur.selectBlocks()
        # cur.select(QtGui.QTextCursor.BlockUnderCursor)
        self.setTextCursor(cur)
        self.cut()
        cur.movePosition(QtGui.QTextCursor.Right)
        self.setTextCursor(cur)
        cur.endEditBlock()
        # if cur.atEnd():
        # cur.deleteChar()

    def SLOT_actionReshapeOneLine(self):
        cur = self.textCursor()
        cur.beginEditBlock()
        for i,bl in enumerate( cur.yieldBlockInSelection(direction=-1)):
            cur.setPosition(bl.position())
            cur.movePosition(QtGui.QTextCursor.EndOfBlock)
            cur.deleteChar()

            charAt = lambda x: str(self.document().characterAt(x))
            while (not cur.atBlockEnd()) and charAt(cur.position()) in [' ','\t']:
                cur.deleteChar()

            if not cur.atBlockEnd():
                cur.insertText(' ')
        cur.movePosition(QtGui.QTextCursor.EndOfBlock)
        self.setTextCursor(cur)
        cur.endEditBlock()

    def SLOT_actionLaunchFindDialog(self):
        """Slot that is called when we have to display the search dialog
        window."""
        self.findDialog.setVisible(True)

    def SLOT_actionDuplicateLine(self):
        cur = self.textCursor()
        cur.beginEditBlock()
        cur.selectBlocks()
        # cur.select(QtGui.QTextCursor.BlockUnderCursor)
        text = str(cur.selectedText())
        if text[0]!=u'\u2029':# strange newline
            text = '\n'+text
        cur.movePosition(QtGui.QTextCursor.EndOfBlock)
        cur.insertText(text)
        cur.endEditBlock()
        self.setTextCursor(cur)

    def SLOT_actionMoveLineUp(self):
        cur = self.textCursor()
        cur.beginEditBlock()
        if not cur.block().previous().isValid() :
            return False
        # cur.select(QtGui.QTextCursor.BlockUnderCursor)
        cur.selectBlocks()
        text = cur.selectedText()
        if not cur.selectionStart()==0:
            text = text[1:]
            ss = True
        else: ss=False
        cur.removeSelectedText()

        cur.movePosition(QtGui.QTextCursor.StartOfBlock,QtGui.QTextCursor.MoveAnchor)
        p = cur.position()
        cur.insertText(text)
        if ss:
            cur.insertBlock()
        cur.setPosition(p)
        cur.movePosition(QtGui.QTextCursor.Right,QtGui.QTextCursor.KeepAnchor,len(text))
        cur.endEditBlock()
        self.setTextCursor(cur)




        # cur = self.textCursor()
        # if not cur.block().previous().isValid() :
        #     return False
        # # cur.select(QtGui.QTextCursor.BlockUnderCursor)
        # cur.selectBlocks()
        # text = cur.selectedText()[1:]
        # cur.removeSelectedText()
        # cur.movePosition(QtGui.QTextCursor.PreviousBlock,QtGui.QTextCursor.MoveAnchor)
        # p = cur.position()
        # cur.insertText(text)
        # cur.insertBlock()
        # cur.setPosition(p)
        # # cur.movePosition(QtGui.QTextCursor.Right,QtGui.QTextCursor.KeepAnchor,len(text))
        # self.setTextCursor(cur)

    def SLOT_actionMoveLineDown(self):
        cur = self.textCursor()
        cur.beginEditBlock()
        if not cur.block().next().isValid() :
            cur.endEditBlock()
            return False
        # cur.select(QtGui.QTextCursor.BlockUnderCursor)
        cur.selectBlocks()
        text=cur.selectedText()
        cur.removeSelectedText()
        if cur.atStart():
            cur.deleteChar()
        else:
            text = text[1:]
            cur.movePosition(QtGui.QTextCursor.NextBlock,QtGui.QTextCursor.MoveAnchor)
        cur.movePosition(QtGui.QTextCursor.EndOfBlock,QtGui.QTextCursor.MoveAnchor)
        cur.insertBlock()
        p = cur.position()
        cur.insertText(text)
        cur.setPosition(p)
        cur.movePosition(QtGui.QTextCursor.StartOfBlock,QtGui.QTextCursor.MoveAnchor)
        cur.movePosition(QtGui.QTextCursor.Right,QtGui.QTextCursor.KeepAnchor,len(text))
        self.setTextCursor(cur)
        cur.endEditBlock()

    def insert_delimiters(self,delim_key,cursor):
        if cursor.hasSelection():
            selectionStart    = cursor.selectionStart()
            selectionEnd    = cursor.selectionEnd()
            position        = cursor.position()
            l1 = len(self.delimiters[delim_key][0])
            l2 = len(self.delimiters[delim_key][1])
            cursor1 = QtGui.QTextCursor(cursor)
            cursor2 = QtGui.QTextCursor(cursor)
            cursor1.setPosition(selectionStart)
            cursor2.setPosition(selectionEnd)
            cursor1.insertText(self.delimiters[delim_key][0])
            cursor2.insertText(self.delimiters[delim_key][1])
            cursor.setPosition(selectionStart+l1,QtGui.QTextCursor.MoveAnchor)
            cursor.setPosition(selectionEnd+l1,QtGui.QTextCursor.KeepAnchor)
            # cursor.setPosition(position+l1,QtGui.QTextCursor.KeepAnchor)

        else:
            cursor.insertText(self.delimiters[delim_key][0])
            cursor.insertText(self.delimiters[delim_key][1])
            cursor.movePosition(QtGui.QTextCursor.Left,QtGui.QTextCursor.MoveAnchor,len(self.delimiters[delim_key][1]))

        return cursor


    def lineNumberAreaWidth(self):
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = 3 + self.fontMetrics().width('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        QtWidgets.QPlainTextEdit.resizeEvent(self,event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))


    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self.lineNumberArea)

        painter.fillRect(event.rect(), QtCore.Qt.lightGray)

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        # Just to make sure I use the right font
        height = self.fontMetrics().height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(blockNumber + 1)
                painter.setPen(QtCore.Qt.black)
                painter.drawText(0, top, self.lineNumberArea.width(), height, QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1


class RMarkdownEditor(QtWidgets.QTextEdit):
    def __init__(self,parent=None):
        QtWidgets.QPlainTextEdit.__init__(self,parent=parent)
        self.highlight = syntax.MarkdownHighlighter(self)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    editor=RMakdownEditor()
    # highlight = syntax.PythonHighlighter(editor.document())

    editor.show()
    sys.exit(app.exec_())
