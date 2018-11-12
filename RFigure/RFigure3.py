# PYTHON 3
""" Unless mentionned otherwise, the code is written by R. Dessalles (Grumpfou).
Published under license GNU General Public License v3.0. Part of the RFigure
project.

Contains RFigureCore and RFigureGui that are dealing with the different files

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
from . import RPickle2
from .RMisc import RDateDisplay, RTextWrap
from PyQt5 import QtGui, QtCore,QtWidgets
from .REditors import RPythonEditor,RMarkdownEditor
from matplotlib.backends.backend_pdf import PdfPages

__version__ = '3'

###################### CONFIG IMPORTATION ##############################
path_to_header = './RFigureConfig/RFigureHeader.py'
file_dir = os.path.realpath(os.path.dirname(__file__))
path_to_header = os.path.join(file_dir,path_to_header)
########################################################################

# matplotlib.pyplot.ion()

class RFigureCore:
	ext = '.rfig3'
	fig_type_list=['eps','pdf','png']
	def __init__(self,dict_variables=None,instructions=None,file_to_run=None,
			commentaries=None,file_split="#! SF_INSTRUCTIONS",
			globals_var=None,d=None,i=None,c=None):
		"""
		This function will save the figure into a propper way, in order to open
		it again.
		- dict_variables [alias: d]: dictionnary that contain the variable
			usefull to plot the figure.
		- instructions [alias: i] : string that contains the python code to
			create the figure.
		- commentaries [alias: c]: some additive string used to comment the
			figure.
		- file_to_run : the file containing the instruction (if
			instructions==None)
		- file_split : if file_to_run, file_split it the string that will
			separate the file_to_run. What will be bollow the first instance of
			file_split will be considered as the instructions. If the
			instructions will ne be encountered, then it take the whole file as
			instructions.
		- globals_var : the globals variables that will be the pool of the
			variables used in figures.

		Usage:
		> d = dict{A=range(10)} # The dict containing the variables of the file
		> i = "plot(A)\ntitle('Example')" # The instrictions to execute
		> comment = "This is a test" # The comments associate with the file
		> rf = RFigureCore(d=d,i=i,c=comment)
		> rf.show() # Show the results
		> rf.save(dirpath='.',filename="Test") # Save the rfig3 file
		> rf.save(dirpath='.',filename="Test",fig_type='pdf') # Save the rfig3 file
		>												   # with the pdf file
		"""
		# Deals with synonyms :
		assert instructions==None or i==None
		assert dict_variables==None or d==None
		assert commentaries==None or c==None

		if i!=None : instructions=i
		if d!=None : dict_variables=d
		if c!=None : commentaries=c

		if instructions==None and file_to_run==None:
			instructions=""

		### We put the commentaries
		if commentaries!=None:
			self.commentaries=commentaries
		else:
			self.commentaries=""

		self.file_split = file_split

		### We put the instructions either from the instructions or from the
		### file
		if file_to_run!=None:

			self.commentaries += 'Script '+ file_to_run+':\n'
			try:
				fid=open(file_to_run)
				self.instructions=fid.read()

			finally:
				fid.close()

		else:
			self.instructions=instructions

		self.clean_instructions() # we clean the instructions

		self.filepath = None
		### We put the variables
		self.globals_var=globals_var
		self.dict_variables= {}
		if dict_variables==None :
			if self.globals_var!=None:
				ll = self.find_list_variables(in_globals_var=True)
				self.input_dict_from_list(ll)

		elif type(dict_variables)==list :
			if self.globals_var!=None:
				self.input_dict_from_list(dict_variables)
			else :
				raise BasicError('If you provide a list of variables, you '+\
						'should provide the global_var dictionary')
		elif type(dict_variables)==dict:
			self.dict_variables=dict_variables
		else:
			raise TypeError('dict_variables should be either a dict either a'+\
					'list of names')


	def execute(self):
		"""
		Will plot the figure.
		"""
		if self.filepath!=None:
			dirpath,_ = os.path.split(self.filepath)
		else:
			dirpath = '.'
		matplotlib.pyplot.close('all')
		if os.path.exists(path_to_header):
			with  open (path_to_header,'r') as fid:
				instructions = fid.read()
		else:
			print("Could not find the path to header")
			instructions = ""

		instructions +='\n\n'

		if not dirpath is None:
			path_to_header_local = os.path.join(dirpath,'./.RFigureHeaderLocal.py')
		if os.path.exists(path_to_header_local):
			fid = open (path_to_header_local,'r')
			try :
				s = fid.read()
				instructions += s
			finally:
				fid.close()


		nb_line_header = len(instructions.split('\n'))
		instructions+=self.instructions


		try:
			exec(instructions,self.dict_variables.copy())
		except Exception as e :
			mess = "Traceback (most recent call last):\n"
			for frame in traceback.extract_tb(sys.exc_info()[2]):
				fname,lineno,fn,text = frame
				if fname == '<string>':
					# removing the number of line of the header
					lineno += -nb_line_header+1
					fname = 'PythonInstructions'
				mess += 'File "'+fname+'", line '+str(lineno)+', in '+fn+\
					'\n\t'+text+'\n'
			mess+= e.__class__.__name__ +':'+str(e)
			raise type(e)(mess)

	def show(self):
		""" Method that execute the code instructions and adds the
		matplotlib.pyplot.show() statement at the end.
		"""
		self.execute()
		matplotlib.pyplot.show()


	def save(self,filepath=None,fig_type=False,formatName=True):
		"""
		Will save the figure in a rfig file. The name of the file will be as
		follow :
				"Figure_" + date + decr + ".rfig"
		- filepath : the filepath where to save the figure
		- decr : short string that qualify the function
		- fig_type : if not False, will save the figure in the corresponding
			format. Should be in [False,'png','pdf','eps']
		- formatName: if True will format the file path: if the filename is
			"test", then the resulting filename will be
			"Figure_20180510_test.rfig3" (with the date corresponding to
			today)
							if False: will only check the extension
		"""
		if filepath is None:
			filepath = self.filepath

		objects = [self.dict_variables,self.instructions]

		RPickle2.save(objects,filepath,self.commentaries,version = __version__)
		paths = [filepath]
		if fig_type:
			paths1 = self.savefig(filepath,fig_type=fig_type)
			paths += paths1
		self.filepath = filepath
		return paths

	def savefig(self,fig_path,fig_type='png'):
		"""Method that will save the figure with the corresponding extention
		- fig_path: the path of where to save the figure the figure
		- fig_type: the type of the figure, should be in ["eps","pdf",'png']
		"""
		assert fig_type in ["eps","pdf",'png']

		dirpath,_=os.path.split(fig_path)
		if fig_type not in self.fig_type_list and not (fig_type is None):
			raise ValueError('fig_type should be in '+str(self.fig_type_list))
		matplotlib.pyplot.ion()
		# self.show()
		self.execute()

		# we make the list of all the figures
		figures=[manager.canvas.figure for manager in \
					matplotlib._pylab_helpers.Gcf.get_all_fig_managers()]

		paths = []
		if fig_type=='png' or fig_type=='eps':
			fig_path,_ = os.path.splitext(fig_path)

			# if there is more than one figure, we will save under the names :
			# Sometitle_00.png , Sometitle_01.png, Sometitle_02.png
			if len(figures)>1:
				to_zfill=np.log10(len(figures))+1
				for i,fig in enumerate(figures):
					nb='_'+str(i).zfill(int(to_zfill))
					f = fig_path+nb+'.'+fig_type
					fig.savefig(f,bbox_inches='tight')
					paths.append(f)
			elif len(figures)>0:
				f = fig_path+'.'+fig_type
				figures[0].savefig(fig_path+'.'+fig_type,bbox_inches='tight')
				paths.append(f)
		elif fig_type=='pdf':
			fig_path,_ = os.path.splitext(fig_path)
			fig_path += '.'+fig_type
			pp = PdfPages(fig_path)
			for fig in figures:
				pp.savefig(fig,bbox_inches='tight',transparent=True)
			pp.close()
			paths.append(fig_path)
		matplotlib.pyplot.close('all')
		matplotlib.pyplot.ioff()
		print ("========== END SAVE =========")
		return paths

	def clean_instructions(self):
		"""Ensure that the instruction are idented at the the first level.
		"""
		current_instructions = self.instructions[:]
		list_lines = current_instructions.split('\n')
		# list_lines = [line.rstrip() for line in list_lines]
		min_tab = np.infty
		for line in list_lines:
			if len(line)>0: #if it is not an emptyline
				i=0
				while i<len(line) and line[i]=='\t' :
					i+=1
				min_tab=np.min([min_tab,i])
				if min_tab==0:
					break

		if min_tab>0 and min_tab!=np.infty:
			for i,line in enumerate(list_lines):
				if len(line)>min_tab:
					list_lines[i]=line[int(min_tab):]
		self.instructions='\n'.join(list_lines)

		self.instructions = self.instructions.split(self.file_split)[-1]

	def find_list_variables(self,in_globals_var=True):
		def empty():pass
		res=[]
		A = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',self.instructions)
		A=set(A)

		if in_globals_var:
			if self.globals_var==None:
				raise BasicError('Can not search in globals_var, it has not '+\
					'been specified.')
			glob_ = self.globals_var
		else:
			glob_ = self.dict_variables.keys()

		for n in A:
			if n in glob_:
				if (not hasattr(glob_[n], '__call__')) and \
					type(glob_[n])!=type(np) :
					# if it is not a function or a type
					res.append(n)
		return res

	def input_dict_from_list(self,list):
		if self.globals_var==None:
			raise BasicError('Can not search in globals_var, it has not '+\
				'been specified.')

		new_dict_variables={}

		for key in list:
			if key not in self.globals_var:
				raise BasicError('The globals_var has no key ' +str(key))
			new_dict_variables[key]=self.globals_var[key]

		self.dict_variables=new_dict_variables


	def open(self,filepath,globals_var=None):
		"""Open the rfig file from filepath"""
		if not os.path.exists(filepath):
			fig_path += self.ext
			assert os.path.exists(filepath), filepath+" does not exist."
		o,c,v = RPickle2.load(filepath)
		assert v>= "2"

		self.commentaries = c
		self.instructions = o[1]
		self.globals_var = globals_var
		self.dict_variables = o[0]
		self.filepath = filepath


	@classmethod
	def load(cls,filepath,globals_var=None):
		"""Return a RFigureCore instance"""
		sfig=cls.__init__()
		sfig.open(filepath)

	@staticmethod
	def update(fig_path,d=None,i=None,c=None,mode='append',fig_type=False):
		"""
		Update the dict_variables of an already existing file:
		Parameters:
			fig_path: str
				The rfig2 file to update.
			d: dict
				The dict to update with.
			i: str
				The instricution to update with.
			c: str
				The commentary to update with.
			mode: str in ['append','replace']
				if mode=='append':
					will update the dict and add instructions and
					commentaries to the allready instructions and
					commentaries
				if mode=='replace':
					will replace the dict, instructions and
					commentaries
		Returns:
			rfig : RFigureCore instance
				the RFigureCore instance with updated dict_variables
		"""
		rfig =  RFigureCore.load(fig_path)

		assert mode in ['append','replace']

		if d!=None:
			if mode == 'append':
				rfig.dict_variables.update(d)
			else:
				rfig.dict_variables = d
		if i!=None:
			if mode == 'append':
				rfig.instructions += i
			else:
				rfig.instructions = i
		if c!=None:
			if mode == 'append':
				rfig.commentaries += c
			else:
				rfig.commentaries = c

		rfig.save(fig_type=fig_type)
		return rfig

	def formatName(self,filepath=None,onlyExt=False,ext=None):
		"""
		Will format the filename. Caution, will not update self.filepath
		"""
		if ext==None: ext=self.ext
		if filepath is None:
			filepath = self.filepath
		dirpath,filename = os.path.split(filepath)
		if not onlyExt:
			if not re.match('^Figure_[0-9]{8}_',filename):
				filename = 'Figure_'+RDateDisplay.cur_date()+'_'+filename
		if not filename.endswith(ext):
			filename,_=os.path.splitext(filename)
			filename += ext

		filepath = os.path.join(dirpath,filename)

		return filepath

class RFigureGui(RFigureCore,QtWidgets.QWidget):
	def __init__(self,parent=None,*args,**kargs):
		"""
		A class that inherit from RFigureCore for the core aspects and QWidget
		for the Gui aspects.
		- dict_variables : a dictionary that contain the string name of the
			variable as key, and the variable itself in value
		- instruction : a string that contain the python code to execute to
			show the figure using the variables contained in dict_variables
		- file_to_run : if the instructions are in a different file
		- commentaries : the comments to add to the file
		- filename : the default name file.
		"""
		QtWidgets.QMainWindow.__init__(self,parent=parent)
		RFigureCore.__init__(self,*args,**kargs)



		sys.stdout = EmittingStream(textWritten=self.outputWritten)
		sys.stderr = EmittingStream(textWritten=self.outputWritten)

		self.editor_python = RPythonEditor()
		# self.editor_python.setSizePolicy( 	QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding))
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
		editor_layout.addWidget(	self.editor_commentaries )
		editor_layout.addWidget(QtWidgets.QLabel("Console:"))
		editor_layout.addWidget(	self.editor_console )
		wid_editor = QtWidgets.QWidget()
		wid_editor.setLayout(editor_layout)
		# self.editor_commentaries.setText(self.commentaries)

		# self.table_variables =  QtWidgets.QTableWidget ( len(self.dict_variables), 1)
		self.table_variables =  TableVariables(saveFigureGui = self)

		actionShow	= QtWidgets.QAction("Show"		,self)
		actionClAll	= QtWidgets.QAction("Close All"	,self)
		actionShow.setShortcuts(QtGui.QKeySequence("Ctrl+M"))
		actionShow.setShortcuts(QtGui.QKeySequence("Ctrl+Return"))
		self.addAction(actionShow)

		button_show = QtWidgets.QPushButton('Show')
		# button_save = QtWidgets.QPushButton('Save')
		button_addVar = QtWidgets.QPushButton('Add variable')
		button_clAll = QtWidgets.QPushButton('Close All')
		button_listVar = QtWidgets.QPushButton('Make list var')
		if self.globals_var==None:
			button_addVar.setEnabled(False)
			button_listVar.setEnabled(False)

		self.comboBox = QtWidgets.QComboBox()
		self.comboBox.addItems(self.fig_type_list+['None'])
		self.comboBox.setCurrentIndex(self.comboBox.findText('pdf'))




		splitter = QtWidgets.QSplitter(self)
		splitter.addWidget	(self.editor_python)
		splitter.addWidget	(wid_editor)
		lay = QtWidgets.QVBoxLayout()
		lay.addWidget(button_show )
		# lay.addWidget(button_save )
		lay.addWidget(button_clAll)
		lay.addWidget(QtWidgets.QLabel("List Variables:"))
		lay.addWidget(self.table_variables)
		lay.addWidget(QtWidgets.QLabel("Export format:"))
		lay.addWidget(self.comboBox)
		wid = QtWidgets.QWidget()
		wid.setLayout(lay)
		splitter.addWidget	(wid)
		total=self.geometry().width()
		splitter.setSizes ( [0.4*total,0.4*total,0.2*total] )

		main_layout = QtWidgets.QVBoxLayout()
		main_layout.addWidget(splitter)
		# wid = QtWidgets.QWidget()
		self.setLayout(main_layout)



		# self.setCentralWidget(wid)

		button_show	  .clicked.connect(self.show)
		# button_save	  .clicked.connect(self.save)
		button_clAll  .clicked.connect(self.closeAll)
		button_addVar .clicked.connect(self.table_variables.addItem)
		button_listVar.clicked.connect(self.make_list_variables)
		actionShow 				.triggered.connect(self.show)
		# actionSave 				.triggered.connect(self.save)
		actionClAll				.triggered.connect(self.closeAll)



		QtWidgets.QMainWindow.show(self)
		self.uploadDataToGui()



	def __del__(self):
		# Restore sys.stdout
		sys.stdout = sys.__stdout__

	def save(self,filepath=None):
		"""
		The saving function called by pushon the 'Save' button.
		Ask for confirmation and automotically save the imgae (png,pdf or eps)
		in the same time.
		"""
		if filepath is None:
			filepath = self.filepath

		assert not filepath is None, "No filepath defined"

		dirpath , _ = os.path.split(filepath)
		if not os.path.exists(dirpath):
			msg = "The dirpath \n%s\n does not exists"%dirpath
			res = QtWidgets.QMessageBox.critical ( self, "Error in dirpath",
				msg,QtWidgets.QMessageBox.Ok)
			return False

		self.instructions	=str(self.editor_python.toPlainText())

		self.commentaries	=str(self.editor_commentaries.toPlainText())
		# filepath = str(self.lineEdit_filepath.text())
		# filepath = self.formatName(filepath,onlyExt=True)
		fig_type 			=str(self.comboBox.currentText())
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

	def open(self,filepath):
		"""Open the rfig file from the corresponding filepath.
		"""
		sf = RFigureCore.open(self,filepath)
		self.uploadDataToGui()


	def show(self):
		"""
		Show the figure using the variables contained in
		self.dict_variables and the instructuion in	self.instructions.
		"""
		self.instructions=str(self.editor_python.toPlainText())

		try:
			print("============ RUN ============")
			RFigureCore.show(self)
		except BaseException as e :

			mess = str(e)
			raise e
		finally:
			print("============ END ============")

	def closeAll(self):
		"""
		Slot that will close all the current matplotlib windows
		"""
		matplotlib.pyplot.close('all')


	@staticmethod
	def loadFromRFigureCore(rfigcore,globals_var=None):
		"""
		Static method used to upgrade a RFigureCore into a RFigureGui
		"""

		return RFigureGui(dict_variables=rfigcore.dict_variables,
								instructions=rfigcore.instructions,
								commentaries=rfigcore.commentaries,
								globals_var=globals_var
								)



	def uploadDataToGui(self):
		""" Update the instructions, the comments and the variables in the
		graphical interface
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



	def make_list_variables(self):
		"""Detect all the variables in the instructions"""
		self.instructions	=str(self.editor_python.text())
		ll = self.find_list_variables(in_globals_var=True)
		self.input_dict_from_list(ll)
		self.table_variables.updateFromDict()

	def closeEvent(self,event):
		"""Reimplementation to close all the figures.
		"""
		matplotlib.pyplot.close('all')
		QtWidgets.QWidget.closeEvent(self,event)

	def outputWritten(self, text):
		"""Appends text to the console"""
		# Maybe QTextEdit.append() works as well, but this is how I do it:
		sys.__stdout__.write(text)
		cursor = self.editor_console.textCursor()
		cursor.movePosition(QtGui.QTextCursor.End)
		cursor.insertText(text)
		self.editor_console.setTextCursor(cursor)
		self.editor_console.ensureCursorVisible()

	def isModified(self):
		return self.editor_commentaries.document().isModified() or self.editor_python.document().isModified()




class RFigureMainWindow(QtWidgets.QMainWindow):
	def __init__(self,*args,**kargs):
		QtWidgets.QMainWindow.__init__(self,*args,**kargs)
		self.rFigureWidget = RFigureGui(self)

		self.actionOpen = QtWidgets.QAction("Open",self)
		self.actionSave = QtWidgets.QAction("Save",self)
		self.actionSaveAs = QtWidgets.QAction("SaveAs",self)
		self.actionClose = QtWidgets.QAction("Close",self)
		self.actionFormatName = QtWidgets.QAction("Format",self)

		self.lineEdit_filepath = QtWidgets.QLineEdit(
							self.rFigureWidget.formatName('./figures/'))
		self.button_formatname = QtWidgets.QPushButton("Format Name")

		### Connections
		self.actionOpen.triggered.connect(self.slotOpen)
		self.actionSave.triggered.connect(self.slotSave)
		self.actionSaveAs.triggered.connect(self.slotSaveAs)
		self.actionClose.triggered.connect(self.close)
		self.lineEdit_filepath.textChanged.connect(self.checkDirpath)
		self.button_formatname.clicked.connect(self.slotFormatName)


		self.actionSave.setShortcuts(QtGui.QKeySequence.Save)
		self.actionSaveAs.setShortcuts(QtGui.QKeySequence.SaveAs)
		self.actionOpen.setShortcuts(QtGui.QKeySequence.Open)
		self.actionClose.setShortcuts(QtGui.QKeySequence.Close)



		toolbar = self.addToolBar('')
		toolbar.addAction(self.actionOpen)
		toolbar.addAction(self.actionSave)
		toolbar.addAction(self.actionSaveAs)
		toolbar.addAction(self.actionClose)



		self.setWindowTitle('RFigureGui 3 : Save matplotlib figure')
		self.setWindowIcon(QtGui.QIcon(os.path.join(file_dir,'images/logo.png')))


		# wid_line = QtWidgets.QWidget()
		# wid_line.setSizePolicy( QtWidgets.QSizePolicy.Expanding,
			# QtWidgets.QSizePolicy.Fixed)
		wid_layout = QtWidgets.QHBoxLayout()
		wid_layout.addWidget(QtWidgets.QLabel("File path:"))
		wid_layout.addWidget(self.lineEdit_filepath)
		wid_layout.addWidget(self.button_formatname)
		# wid_line.setLayout(wid_layout)

		main_layout = QtWidgets.QVBoxLayout()
		main_layout.addWidget(self.rFigureWidget)
		main_layout.addLayout(wid_layout)


		centralWidget = QtWidgets.QWidget()
		centralWidget.setLayout(main_layout)

		self.setCentralWidget(centralWidget)


		self.checkDirpath()




	@QtCore.pyqtSlot()
	def slotOpen(self,filepath=None):
		self.checkBeforeClose()
		if filepath is None:
			filepath = QtWidgets.QFileDialog().getOpenFileName(self)[0]
			if not filepath:
				return False
		self.rFigureWidget.open(filepath)
		self.lineEdit_filepath.setText(filepath)


	@QtCore.pyqtSlot()
	def slotSave(self,filepath=None):
		if filepath is None:
			filepath = str(self.lineEdit_filepath.text()).strip()
			if len(filepath)==0:
				return self.slotSaveAs()
		filepath = self.rFigureWidget.formatName(filepath,onlyExt=True)
		self.rFigureWidget.save(filepath)
		self.lineEdit_filepath.setText(filepath)

	@QtCore.pyqtSlot()
	def slotSaveAs(self):
		filepath = QtWidgets.QFileDialog().getSaveFileName(self)[0]
		if not filepath:
			return False
		self.slotSave(filepath)

	@QtCore.pyqtSlot()
	def slotFormatName(self):
		filepath = str(self.lineEdit_filepath.text())
		filepath = self.rFigureWidget.formatName(filepath)
		self.lineEdit_filepath.setText(filepath)


	def checkBeforeClose(self):
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
		"""Check if we have changed something without saving"""
		res=self.checkBeforeClose()
		if (res == QtWidgets.QMessageBox.Yes) or (res == QtWidgets.QMessageBox.No):
			event.accept()
		else:
			event.ignore()

	def checkDirpath(self):
		filepath = str(self.lineEdit_filepath.text())
		dirpath,_ = os.path.split(filepath)
		palette = self.lineEdit_filepath.palette()
		if os.path.exists(os.path.abspath(dirpath)):
			palette.setColor( QtGui.QPalette.Text, QtCore.Qt.green)
		else:
			palette.setColor( QtGui.QPalette.Text, QtCore.Qt.red)
		self.lineEdit_filepath.setPalette(palette)
		self.rFigureWidget.filepath = filepath



class TableVariables(QtWidgets.QTableWidget):
	"""
	This widget is a re-implementation of the QTableWidget. It deals with
	the variables that have to be saved with the figure.
	"""

	def __init__(self,saveFigureGui,list_var=None):
		if list_var==None: list_var=[]
		QtWidgets.QTableWidget.__init__ (self, len(list_var), 2)
		# self.globals_var=globals_var
		self.saveFigureGui=saveFigureGui
		# self.connect(SIGNAL(returnPressed()),ui->homeLoginButton,SIGNAL(clicked()))

	def keyPressEvent(self,event):
		if event.key()==QtCore.Qt.Key_Delete:
			self.deleteItem(self.currentRow ())
		if event.key()==QtCore.Qt.Key_F2:
			self.renameItem(self.currentRow ())


	def deleteItem(self,row):
		msg = "Are you sure you want to delete the variable <"+self.item(row,0).text()+">?"
		res = QtWidgets.QMessageBox.question (self, "Delete variable", msg,QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
		if (res == QtWidgets.QMessageBox.Yes):
			self.saveFigureGui.dict_variables.pop(str(self.item(row,0).text()))
			self.updateFromDict()

	def renameItem(self,row):
		old_k = str(self.item(row,0).text())
		msg = "How rename the variable <"+self.item(row,0).text()+">?"
		res = QtWidgets.QInputDialog.getText(self, "Rename variable",msg,text =old_k)

		if res[1] and str(res[0])!='' and res[0]!=old_k:
			if str(res[0]) in self.saveFigureGui.dict_variables.keys():
				msg = "The name of the variable <"+str(res[0])+"> is allready used."
				res = QtWidgets.QMessageBox.critical(self, "Rename variable", msg)
			else:
				v = self.saveFigureGui.dict_variables.pop(old_k)
				self.saveFigureGui.dict_variables[str(res[0])] = v
				self.updateFromDict()

	def addItem(self):
		if self.saveFigureGui.globals_var!=None:
			text, ok  = QInputDialog.getText(self,"Name the variable","Please give the variable's name")
			if ok:
				text=str(text)
				text=text.strip()
				if text in self.saveFigureGui.dict_variables.keys():
					msg = "The variable <"+text+"> already exists!"
					QtWidgets.QMessageBox.critical(self, "Variable exists", msg)
					self.addItem()
				elif text not in self.saveFigureGui.globals_var.keys():
					msg = "The variable <"+text+"> is not in the pool of variables!"
					QtWidgets.QMessageBox.critical(self, "Variable exists", msg)
					self.addItem()
				else :
					self.saveFigureGui.dict_variables[text]=self.saveFigureGui.globals_var[text]
					msg="We added the variable <"+text+"> of the type <"+\
							str(type(self.saveFigureGui.globals_var[text]))+">."
					QtWidgets.QMessageBox.information(self, "Variable exists", msg)
					self.updateFromDict()

		else:
			msg= "No dictonary of global variables has been provided."
			QtWidgets.QMessageBox.critical(self, "Variable exists", msg)

	def updateFromDict(self):
		self.setRowCount(len(self.saveFigureGui.dict_variables))
		keys = list(self.saveFigureGui.dict_variables.keys())
		keys.sort()
		items = [(k,self.saveFigureGui.dict_variables[k]) for k in keys]
		for i,(k,v) in enumerate(items):
			self.setItem(i,0,QtWidgets.QTableWidgetItem(k))
			self.setItem(i,1,QtWidgets.QTableWidgetItem(str(type(v))))

class EmittingStream(QtCore.QObject):

	textWritten = QtCore.pyqtSignal(str)

	def write(self, text):
		self.textWritten.emit(str(text))

def getInstruction(fig_path):
	rf = RFigureCore.load(fig_path)
	res = rf.instructions[:]
	del rf
	return res

def getDictVariables(fig_path):
	rf = RFigureCore.load(fig_path)
	res = rf.dict_variables
	return res

def	getCommentaries(fig_path):
	rf = RFigureCore.load(fig_path)
	res = rf.commentaries
	return res

def convert_1_to_3(file,gui=False):
	"""
	This function will read a version 1 RFigure and return a version RFigure2
	instance:
	- gui : if False, will retrun a RFigureCore instance
			if True, will retrun a RFigureGui instance
	"""
	import RFigure1
	rf = RFigure1.RFigureCore.load(file)
	res = RFigureCore(	dict_variables	= rf.dict_variables	,
						instructions	= rf.instructions	,
						commentaries	= rf.commentaries	,
			)
	if gui:
		res = RFigureGui.loadFromRFigureCore(res,file)
	return res

def convert_2_to_3(file,gui=False):
	"""
	This function will read a version 2 RFigure and return a version RFigure3
	instance:
	- gui : if False, will retrun a RFigureCore instance
			if True, will retrun a RFigureGui instance
	"""
	file1 = RPickle2.convert_1_to_2(file,ext=RFigureCore.ext)
	if gui:
		return RFigureGui.load(file1)
	else:
		return RFigureCore.load(file1)

if QtWidgets.QApplication.instance()==None:
	import sys
	app = QtWidgets.QApplication(sys.argv)
else:
	app = QtWidgets.QApplication.instance()


def main(argv):
	iconpath = '/home/dessalles/.local/share/icons/hicolor/256x256/rfigure.ico'
	app.setWindowIcon(QtGui.QIcon(iconpath))

	sf=QtWidgets.QWidget()
	# def my_excepthook(type, value, tback):
	# 	res=type.__name__+":"+str(value)
	# 	if not (type.__name__=='SystemExit' and res=='SystemExit:0'):
	# 		msgBox=QtWidgets.QMessageBox.critical(sf, type.__name__, type.__name__+'\n'+res+'\n'+tback)
	# 	sys.__excepthook__(type, value, tback)
	# 	msgBox.show()
	if len(argv)>1:
		f = ' '.join(argv[1:])
		if f[-len(RFigureCore.ext):]== RFigureCore.ext:
			sf=RFigureMainWindow()
			sf.slotOpen(f)
		elif f[-len(RFigureCore.ext):]== '.rfig2':
			sf = convert_2_to_3(f,gui=True)
		else:
			sf = convert_1_to_3(f,gui=True)
		sf.show()
	else:
		# sf=RFigureGui(instructions='',dict_variables={})
		sf=RFigureMainWindow()
		sf.show()
	# sys.excepthook = my_excepthook
	sys.exit(app.exec_())




if __name__ == '__main__':
	main(sys.argv)
