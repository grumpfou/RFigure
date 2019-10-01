# PYTHON 3
""" Unless mentionned otherwise, the code is written by R. Dessalles (Grumpfou).
Published under license GNU General Public License v3.0. Part of the RFigure
project.
"""
import matplotlib
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    matplotlib.use('Qt5Agg')

import matplotlib.pyplot
# matplotlib.pyplot.ion()
matplotlib.pyplot.show._needmain = False
import numpy as np
import os
import tempfile
import re
import traceback
import sys
from .RFigureMisc import  RTextWrap
from PyQt5 import QtGui, QtCore,QtWidgets
from .REditors import RPythonEditor,RMarkdownEditor
from matplotlib.backends.backend_pdf import PdfPages
from .RFigureCore import RFigureCore,__version__

###################### CONFIG IMPORTATION ##############################
path_to_header = './RFigureConfig/RFigureHeader.py'
file_dir = os.path.realpath(os.path.dirname(__file__))
path_to_header = os.path.join(file_dir,path_to_header)
########################################################################

class RFigureGui(RFigureCore,QtWidgets.QWidget):
    def __init__(self,parent=None,*args,**kargs):
        """
        A class that inherit from RFigureCore for the core aspects and QWidget
        for the Gui aspects.

        Parameters
        ----------
        d,i,c,file_split,filepath :
            see RFigureCore docuementation
        parent : QtGui.QWidget
            the parent widget if this widget
        """
        QtWidgets.QWidget.__init__(self,parent=parent)
        RFigureCore.__init__(self,*args,**kargs)

        sys.stdout = EmittingStream(textWritten=self.outputWritten)
        sys.stderr = EmittingStream(textWritten=self.outputWritten)

        self.editor_python = RPythonEditor()
        # self.editor_python.setSizePolicy(     QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding))
        # self.editor_python.setText(self.instructions)
        self.editor_commentaries = RMarkdownEditor()
        self.editor_console = QtWidgets.QTextEdit()
        # self.editor_console.setTextBackgroundColor(QtCore.Qt.black)
        # self.editor_console.setTextColor(QtCore.Qt.white)
        p = self.editor_console.palette()
        p.setColor(QtGui.QPalette.Base,QtCore.Qt.black)
        p.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        self.editor_console.setPalette(p)
        # self.editor_console.setReadOnly(True)

        editor_layout = QtWidgets.QVBoxLayout()
        editor_layout.addWidget(QtWidgets.QLabel("Commentaries:"))
        editor_layout.addWidget(    self.editor_commentaries )
        editor_layout.addWidget(QtWidgets.QLabel("Console:"))
        editor_layout.addWidget(    self.editor_console )
        wid_editor = QtWidgets.QWidget()
        wid_editor.setLayout(editor_layout)
        # self.editor_commentaries.setText(self.commentaries)

        # self.table_variables =  QtWidgets.QTableWidget ( len(self.dict_variables), 1)
        self.table_variables =  TableVariables(saveFigureGui = self)
        self.table_variables.horizontalHeader().setStretchLastSection(True)

        actionShow    = QtWidgets.QAction("Show"        ,self)
        actionClAll    = QtWidgets.QAction("Close All"    ,self)
        actionShow.setShortcuts(QtGui.QKeySequence("Ctrl+M"))
        actionShow.setShortcuts(QtGui.QKeySequence("Ctrl+Return"))
        self.addAction(actionShow)

        button_show = QtWidgets.QPushButton('Show')
        button_clAll = QtWidgets.QPushButton('Close All')

        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.addItems(self.fig_type_list+['None'])
        self.comboBox.setCurrentIndex(self.comboBox.findText('pdf'))

        splitter = QtWidgets.QSplitter(self)
        splitter.addWidget    (self.editor_python)
        splitter.addWidget    (wid_editor)
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(button_show )
        # lay.addWidget(button_save )
        lay.addWidget(button_clAll)
        lay.addWidget(QtWidgets.QLabel("List Variables:"))
        lay.addWidget(self.table_variables)
        # lay.addWidget(QtWidgets.QLabel("Export format:"))
        # lay.addWidget(self.comboBox)
        wid = QtWidgets.QWidget()
        wid.setLayout(lay)
        splitter.addWidget    (wid)
        total=self.geometry().width()
        splitter.setSizes ( [0.4*total,0.4*total,0.2*total] )

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(splitter)
        # wid = QtWidgets.QWidget()
        self.setLayout(main_layout)

        button_show      .clicked.connect(self.show)
        # button_save      .clicked.connect(self.save)
        button_clAll  .clicked.connect(self.closeAll)
        actionShow                 .triggered.connect(self.show)
        # actionSave                 .triggered.connect(self.save)
        actionClAll                .triggered.connect(self.closeAll)

        QtWidgets.QMainWindow.show(self)
        self.uploadDataToGui()

    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__

    def save(self,filepath=None):
        """
        The saving function called by the `Save` button.
        Ask for confirmation and automotically save the image (png,pdf or eps)
        at the same time.

        Paramters
        ---------
        filepath : str
            the file where to save the figure (by default, take the
            `self.filepath` attribute)
        """
        if filepath is None:
            filepath = self.filepath

        assert not filepath is None, "No filepath defined"

        dirpath , _ = os.path.split(filepath)
        if dirpath=="":
            dirpath    = '.'
        if not os.path.exists(dirpath) :
            msg = "The dirpath \n%s\n does not exists"%dirpath
            res = QtWidgets.QMessageBox.critical ( self, "Error in dirpath",
                msg,QtWidgets.QMessageBox.Ok)
            return False

        self.instructions    =str(self.editor_python.toPlainText())

        self.commentaries    =str(self.editor_commentaries.toPlainText())
        # filepath = str(self.lineEdit_filepath.text())
        # filepath = self.formatName(filepath,onlyExt=True)
        fig_type             =str(self.comboBox.currentText())
        if fig_type=='None': fig_type=None

        msg= "We are going to save the figure in \n"+filepath
        msg = RTextWrap(str(msg))

        res = QtWidgets.QMessageBox.question ( self, "Saving confirmation",
            msg,QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)

        if (res == QtWidgets.QMessageBox.Yes):

            res = RFigureCore.save(self,filepath, fig_type=fig_type)
            if not res:
                d,_ = os.path.split(filepath)
                msg = "The directory %s does not exist."%d
                QtWidgets.QMessageBox.information ( self, "No saving", msg)
            else:
                self.editor_python.document().setModified(False)
                self.editor_commentaries.document().setModified(False)

    def exportFig(self,filepath,**kargs):
        fig_type             =str(self.comboBox.currentText())
        if fig_type=='None':
            return False

        filepath1 = os.path.splitext(filepath)[0]
        msg= "We are going to export the figure in \n"+filepath1+'.'+fig_type
        msg = RTextWrap(str(msg))

        res = QtWidgets.QMessageBox.question ( self, "Export confirmation",
            msg,QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)

        if (res == QtWidgets.QMessageBox.Yes):
            res = RFigureCore.savefig(self,filepath, fig_type=fig_type)
        return res

    def open(self,filepath):
        """Open the rfig file from the corresponding filepath.

        Paramters
        ---------
        filepath : str
            the file path of the figure to open
        """
        sf = RFigureCore.open(self,filepath)
        self.uploadDataToGui()


    def show(self):
        """
        Show the figure using the variables contained in
        `self.dict_variables` and the instructuion in `self.instructions`.
        """
        self.instructions=str(self.editor_python.toPlainText())

        print("============ RUN ============")
        RFigureCore.show(self,print_errors=True)
        print("============ END ============")
        # try:
        # except BaseException as e :
        #
        #     mess = str(e)
        #     raise e
        # finally:
        #     print("============ END ============")

    def closeAll(self):
        """
        Slot that will close all the current matplotlib windows
        """
        matplotlib.pyplot.close('all')


    @staticmethod
    def loadFromRFigureCore(rfigcore):
        """
        Static method used to upgrade a RFigureCore into a RFigureGui
        """

        return RFigureGui(dict_variables=rfigcore.dict_variables,
                                instructions=rfigcore.instructions,
                                commentaries=rfigcore.commentaries,
                                filepath=rfigcore.filepath,
                                )



    def uploadDataToGui(self):
        """ Update the attributes `self.instructions`, `self.commentaties`,
        `self.dict_variables` in the graphical interface.
        """
        self.table_variables.setRowCount(len(self.dict_variables))
        for i,k in enumerate(self.dict_variables.keys()):
            self.table_variables.setItem(i,0,QtWidgets.QTableWidgetItem(k))
        self.table_variables.updateFromDict()
        self.editor_python.setPlainText(self.instructions)
        self.editor_commentaries.setText(self.commentaries)
        self.editor_python.document().setModified(False)
        self.editor_commentaries.document().setModified(False)
        # self.lineEdit_filename.setText(self.filename)


    def closeEvent(self,event):
        """ Reimplementation of the method to close all the matplotlib figures
        before closing the widget.

        Parameters
        ----------
        event : QEvent
            the close event that needs to be handled
        """
        matplotlib.pyplot.close('all')
        QtWidgets.QWidget.closeEvent(self,event)

    def outputWritten(self, text):
        """Appends text to the terminal console.

        Parameters
        ----------
        text : str
            Text to add to the console.
        """
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        sys.__stdout__.write(text)
        cursor = self.editor_console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.editor_console.setTextCursor(cursor)
        self.editor_console.ensureCursorVisible()

    def isModified(self):
        """ Determine if the figure instructions or commentaries have been
        modified.

        Returns
        -------
        state : bool
            True if the instructions or commentaries have been modified since
            last save.
        """
        return self.editor_commentaries.document().isModified() or self.editor_python.document().isModified()


class RFigureMainWindow(QtWidgets.QMainWindow):
    def __init__(self,*args,**kargs):
        """ Main window of teh graphical interface. It's central widget is the
        `RFigureGui` instance. Contains slots to save, open, close, etc.
        """
        QtWidgets.QMainWindow.__init__(self,*args,**kargs)
        self.rFigureWidget = RFigureGui(self)

        dict_icons = dict(open="003-folder.png",
                          save="002-save.png",
                          saveas="008-saveas.png",
                          export="004-export.png",
                          close="005-cross.png",
                          about="007-question.png",
                            )
        dict_icons = {k:os.path.join(file_dir,'images',v) for k,v in dict_icons.items()}
        dict_icons = {k:QtGui.QIcon(v) for k,v in dict_icons.items()}

        self.actionOpen = QtWidgets.QAction(dict_icons['open'],"Open",self)
        self.actionSave = QtWidgets.QAction(dict_icons['save'],"Save",self)
        self.actionSaveAs = QtWidgets.QAction(dict_icons['saveas'],"SaveAs",self)
        self.actionExport = QtWidgets.QAction(dict_icons['export'],"Export",self)
        self.actionClose = QtWidgets.QAction(dict_icons['close'],"Close",self)
        self.actionAbout= QtWidgets.QAction(dict_icons['about'],"About",self)
        self.actionFormatName = QtWidgets.QAction("Format",self)


        self.lineEdit_filepath = QtWidgets.QLineEdit(
                self.rFigureWidget.formatExt(
                    self.rFigureWidget.formatName('./untitled')))
        self.button_formatname = QtWidgets.QPushButton("Format Name")

        ### Connections
        self.actionOpen.triggered.connect(self.slotOpen)
        self.actionSave.triggered.connect(self.slotSave)
        self.actionSaveAs.triggered.connect(self.slotSaveAs)
        self.actionExport.triggered.connect(self.slotExport)
        self.actionClose.triggered.connect(self.close)
        self.lineEdit_filepath.textChanged.connect(self.checkDirpath)
        self.button_formatname.clicked.connect(self.slotFormatName)
        self.actionAbout.triggered.connect(self.slotAbout)
        self.rFigureWidget.comboBox.currentIndexChanged[str].connect(self.checkExport)

        self.rFigureWidget.editor_python.textChanged.connect(lambda *args,**kargs:self.actionSave.setEnabled(True))


        self.actionSave.setShortcuts(QtGui.QKeySequence.Save)
        self.actionSaveAs.setShortcuts(QtGui.QKeySequence.SaveAs)
        self.actionOpen.setShortcuts(QtGui.QKeySequence.Open)
        self.actionClose.setShortcuts(QtGui.QKeySequence.Close)
        self.actionAbout.setShortcuts(QtGui.QKeySequence.HelpContents)

        toolbar = self.addToolBar('')
        toolbar.addAction(self.actionOpen)
        toolbar.addAction(self.actionSave)
        toolbar.addAction(self.actionSaveAs)
        toolbar.addAction(self.actionExport)
        toolbar.addWidget(QtWidgets.QLabel("Export format: "))
        toolbar.addWidget(self.rFigureWidget.comboBox)
        toolbar.addAction(self.actionClose)
        toolbar.addAction(self.actionAbout)
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        self.setWindowTitle('RFigureGui %s : Save matplotlib figure'%__version__)
        self.setWindowIcon(QtGui.QIcon(os.path.join(file_dir,'images','logo.png')))

        wid_layout = QtWidgets.QHBoxLayout()
        wid_layout.addWidget(QtWidgets.QLabel("File path:"))
        wid_layout.addWidget(self.lineEdit_filepath)
        wid_layout.addWidget(self.button_formatname)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.rFigureWidget)
        main_layout.addLayout(wid_layout)


        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(main_layout)

        self.setCentralWidget(centralWidget)

        self.checkDirpath()

    @QtCore.pyqtSlot()
    def slotOpen(self,filepath=None):
        """Slot to open a figure

        Parameters
        ----------
        filepath : str
            The file path to open. If None, ask the user which file to open.
        """
        self.checkBeforeClose()
        if filepath is None:
            filepath = QtWidgets.QFileDialog().getOpenFileName(self)[0]
            if not filepath:
                return False
        self.rFigureWidget.open(filepath)
        self.lineEdit_filepath.setText(filepath)
        self.actionSave.setEnabled(False)


    @QtCore.pyqtSlot()
    def slotSave(self,filepath=None):
        """Slot to save the figure (and export it)

        Parameters
        ----------
        - filepath : str
            The file path where to save the figure.
            If None, either take the string in `self.lineEdit_filepath`, or
            if `self.lineEdit_filepath` is empty, asks the user.
        """

        if filepath is None:
            filepath = str(self.lineEdit_filepath.text()).strip()
            if len(filepath)==0:
                return self.slotSaveAs()
        filepath = self.rFigureWidget.formatExt(filepath)
        self.rFigureWidget.save(filepath)
        self.lineEdit_filepath.setText(filepath)
        self.actionSave.setEnabled(False)

    @QtCore.pyqtSlot()
    def slotExport(self,filepath=None):
        """Slot to only export the figure

        Parameters
        ----------
        - filepath : str
            The file path where to export the figure. If None, either take the
            string in `self.lineEdit_filepath`, or if `self.lineEdit_filepath`
            is empty, asks the user. Changes the extention to make it correspond
            to the one in the `self.rFigureWidget.comboBox`.
        """

        if filepath is None:
            filepath = str(self.lineEdit_filepath.text()).strip()
            if len(filepath)==0:
                return self.slotSaveAs()
        filepath = self.rFigureWidget.formatExt(filepath)
        self.rFigureWidget.exportFig(filepath)
        self.lineEdit_filepath.setText(filepath)


    @QtCore.pyqtSlot()
    def slotSaveAs(self):
        """Slot to save the figure by asking the user where to save it.
        """

        filepath = QtWidgets.QFileDialog().getSaveFileName(self)[0]
        if not filepath:
            return False
        self.slotSave(filepath)

    @QtCore.pyqtSlot()
    def slotFormatName(self):
        """ Format the current filepath to the format
                    Figure_YYYYMMDD_foo.rfig3
        """
        filepath = str(self.lineEdit_filepath.text())
        filepath = self.rFigureWidget.formatExt(filepath)
        filepath = self.rFigureWidget.formatName(filepath)
        self.lineEdit_filepath.setText(filepath)

    @QtCore.pyqtSlot()
    def slotAbout(self):
        text = (
          "<p>RFigure is a software dedicated to the edition of figures using "
          "Python and Matplotlib. I is mainly written by Renaud Dessalles "
          "(Grumpfou) and distributed under the licence GNU General Public "
          "License v3.0 (unless some part of the code when specified otherwise, "
          "written by somebody else)</p>\n\n"

          "<p>Sources, bug reporting, help are available on "
          "<a href=\"http://github.com/grumpfou/RFigure\">http://github.com/grumpfou/RFigure</a>.</p>"
          "<p>Licenses of the icons available "
          "<a href=\"https://github.com/grumpfou/RFigure/blob/master/RFigure/images/icons_credits.md\">here.</p>"
            )
        msgBox = QtWidgets.QMessageBox()
        # QtCore.Qt.convertFromPlainText(text)
        msgBox.setTextFormat(QtCore.Qt.RichText)
        # tect =  QtCore.Qt.convertFromPlainText(text)
        msgBox.about(self, "About RFigure",text)


    def checkBeforeClose(self):
        """Checks if the document has been modified before closing. If it has,
        ask the user if they wants to save it.

        Returns
        -------
        res : QtWidgets.QMessageBox status
            the QtWidgets.QMessageBox status (QtWidgets.QMessageBox.Yes or
            QtWidgets.QMessageBox.No) depending on the answer
        """
        if self.rFigureWidget.isModified():
            res=QtWidgets.QMessageBox.question(
                    self,
                    "Modification", "Do you want to save the modifications",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | \
                    QtWidgets.QMessageBox.Cancel
                    )
            if (res == QtWidgets.QMessageBox.Yes):
                self.slotSave()
            return res
        return QtWidgets.QMessageBox.Yes

    def closeEvent(self, event):
        """Checks if we have changed something without saving

        Parameters
        ----------
        event : QEvent
            the event to handle
        """
        res=self.checkBeforeClose()
        if (res == QtWidgets.QMessageBox.Yes) or (res == QtWidgets.QMessageBox.No):
            event.accept()
        else:
            event.ignore()

    def checkDirpath(self):
        """Checks if the directory of the filepath in `self.lineEdit_filepath`
        is an existing directory. If it is, colors `self.lineEdit_filepath` in
        green otherwise in red.
        """
        filepath = str(self.lineEdit_filepath.text())
        dirpath,_ = os.path.split(filepath)
        palette = self.lineEdit_filepath.palette()
        if os.path.exists(os.path.abspath(dirpath)):
            palette.setColor( QtGui.QPalette.Text, QtCore.Qt.darkGreen)
        else:
            palette.setColor( QtGui.QPalette.Text, QtCore.Qt.red)
        self.lineEdit_filepath.setPalette(palette)
        self.rFigureWidget.filepath = filepath

    def checkExport(self,res):
        """Chacks if the combo of the fig_type is to None. If it is the case
        it disables the `self.actionExport`.

        Parameters
        ----------
        res : str
            the content of `self.rFigureWidget.comboBox`
        """
        if res == 'None':
            self.actionExport.setEnabled(False)
        else:
            self.actionExport.setEnabled(True)



class TableVariables(QtWidgets.QTableWidget):
    """
    This widget is a re-implementation of the QTableWidget. It deals with
    the variables that have to be saved with the figure.
    """

    def __init__(self,saveFigureGui,list_var=None):
        if list_var==None: list_var=[]
        QtWidgets.QTableWidget.__init__ (self, len(list_var), 3)
        self.setHorizontalHeaderLabels(["Name","Type","Size"])
        self.saveFigureGui=saveFigureGui
        # self.connect(SIGNAL(returnPressed()),ui->homeLoginButton,SIGNAL(clicked()))

    # def keyPressEvent(self,event):

    #     if event.key()==QtCore.Qt.Key_Delete:
    #         self.deleteItem(self.currentRow ())
    #     if event.key()==QtCore.Qt.Key_F2:
    #         self.renameItem(self.currentRow ())


    # def deleteItem(self,row):
    #     msg = "Are you sure you want to delete the variable <"+self.item(row,0).text()+">?"
    #     res = QtWidgets.QMessageBox.question (self, "Delete variable", msg,QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
    #     if (res == QtWidgets.QMessageBox.Yes):
    #         self.saveFigureGui.dict_variables.pop(str(self.item(row,0).text()))
    #         self.updateFromDict()
    #
    # def renameItem(self,row):
    #     old_k = str(self.item(row,0).text())
    #     msg = "How rename the variable <"+self.item(row,0).text()+">?"
    #     res = QtWidgets.QInputDialog.getText(self, "Rename variable",msg,text =old_k)
    #
    #     if res[1] and str(res[0])!='' and res[0]!=old_k:
    #         if str(res[0]) in self.saveFigureGui.dict_variables.keys():
    #             msg = "The name of the variable <"+str(res[0])+"> is allready used."
    #             res = QtWidgets.QMessageBox.critical(self, "Rename variable", msg)
    #         else:
    #             v = self.saveFigureGui.dict_variables.pop(old_k)
    #             self.saveFigureGui.dict_variables[str(res[0])] = v
    #             self.updateFromDict()
    #

    def updateFromDict(self):
        """Function called when a new `dict_variables` has been introduced in
        the `RFigureGui`. It updates the list of varibales in the table.
        """
        self.setRowCount(len(self.saveFigureGui.dict_variables))
        keys = list(self.saveFigureGui.dict_variables.keys())
        keys.sort()
        items = [(k,self.saveFigureGui.dict_variables[k]) for k in keys]
        # Compute the size of teh variables
        for i,(k,v) in enumerate(items):
            self.setItem(i,0,QtWidgets.QTableWidgetItem(k))
            self.setItem(i,1,QtWidgets.QTableWidgetItem(str(type(v))))
            def get_length(var):
                res = 0
                if type(var) == list or type(var) == tuple:
                    for x in var: res+=get_length(x)
                elif type(var) == dict:
                    for x,y in var.items(): res+=get_length(x)+get_length(y)
                elif type(var) == np.ndarray :
                    # the method `take` is to deal with the case where
                    # var.shape==(,) (singleton):
                    res = var.size*get_length(var.take(0))
                else:
                    try:
                        res = len(var) # string
                    except TypeError: #int, float, etc.
                        res = 1
                return res
            len_ = get_length(v)
            if len_>1000:
                len_ = "%.0e"%len_
            self.setItem(i,2,QtWidgets.QTableWidgetItem(str(len_)))

class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


if QtWidgets.QApplication.instance()==None:
    import sys
    app = QtWidgets.QApplication(sys.argv)
else:
    app = QtWidgets.QApplication.instance()


def main(argv=None):
    if argv is None: argv=[]
    iconpath = os.path.join(os.path.split(__file__)[0],'logo.png')
    app.setWindowIcon(QtGui.QIcon(iconpath))

    sf=QtWidgets.QWidget()

    if len(argv)>1:
        f = ' '.join(argv[1:])
        sf=RFigureMainWindow()
        sf.slotOpen(f)

        sf.show()
    else:
        sf=RFigureMainWindow()
        sf.show()
    sys.exit(app.exec_())




if __name__ == '__main__':
    main(sys.argv)
