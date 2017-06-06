# PYTHON 3
""" Unless mentionned otherwise, the code is written by R. Dessalles (Grumpfou).
Published under license GNU General Public License v3.0. Part of the RFigure
project.

Contains RFigureCore and RFigureGui that are dealing with the different files

"""
import matplotlib
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
import RPickle2
from RMisc import RDateDisplay, RTextWrap
from PyQt5 import QtGui, QtCore,QtWidgets
from REditors import RPythonEditor,RMarkdownEditor
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
			globals_var=None,d=None,i=None,c=None,
			filename=None,dirpath=None):
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
		print ("cuiou")
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

		### We put the filename, and dirpath
		if dirpath==None:self.dirpath='./figures/'
		else: self.dirpath=dirpath.strip()
		if self.dirpath == "": self.dirpath='.'

		if filename==None	:self.filename=''
		else: self.filename=filename
		# if globals_var==None: globals_var=globals()

	def show(self):
		"""
		Will plot the figure.
		"""
		matplotlib.pyplot.close('all')
		fid = open (path_to_header,'r')
		try :
			instructions = fid.read()
		finally:
			fid.close()
		instructions +='\n\n'

		path_to_header_local = os.path.join(self.dirpath,'./.RFigureHeaderLocal.py')
		if os.path.exists(path_to_header_local):
			fid = open (path_to_header_local,'r')
			try :
				s = fid.read()
				instructions += s
			finally:
				fid.close()


		nb_line_header = len(instructions.split('\n'))
		instructions+=self.instructions

		# tf = tempfile.NamedTemporaryFile(delete=False,encoding='utf-8',mode='w')
		# tf.write(instructions)
		# tf.close()

		try:
			# execfile(tf.name,self.dict_variables.copy())
			exec(instructions,self.dict_variables.copy())
		except Exception as e :
			# if hasattr(e,"lineno"):
			# 	e.lineno -= nb_line_header-1
			# This is because I want to give the good line number of the error.
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

		matplotlib.pyplot.show()

	def save(self,dirpath=None,filename=None,fig_type=False,formatName=True):
		"""
		Will save the figure in a rfig file. The name of the file will be as
		follow :
				"Figure_" + date + decr + ".rfig"
		- dirpath : the directory where to save the function
		- decr : short string that qualify the function
		- fig_type : if not False, will save the figure in the corresponding
			format. Should be in [False,'png','pdf','eps']
		- formatName: if True will format the file path: if the filename is
			"test", then the resulting filename will be
			"Figure_20180510_test.rfig3" (with the date corresponding to
			today)
							if False: will only check the extension
		"""
		if filename==None : filename=self.filename
		else: self.filename=filename
		if dirpath==None: dirpath=self.dirpath
		else: self.dirpath=dirpath


		objects = [self.dict_variables,self.instructions]


		if not os.path.exists(dirpath):
			raise IOError('The dirpath '+dirpath+' does not exists')
			return False

		filename =  self.formatName(onlyExt=(not formatName))

		f = os.path.join(dirpath,filename)
		RPickle2.save(objects,f,self.commentaries,version = __version__)
		paths = [f]
		if fig_type:
			paths1 = self.savefig(os.path.join(dirpath,filename),fig_type=fig_type)
			paths += paths1
		return paths

	def savefig(self,fig_path,fig_type='png'):

		if fig_type not in self.fig_type_list:
			raise ValueError('fig_type should be in '+str(self.fig_type_list))
		matplotlib.pyplot.ion()
		self.show()

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

		ii =  self.instructions.find(self.file_split)
		if ii>0:
			self.instructions=self.instructions[ii:]
			f = self.instructions[:ii]
			f = f.replace('\n','\n>>> ')

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

	@classmethod
	def load(cls,fig_path,globals_var=None):
		"""Return a RFigureCore instance"""

		if not os.path.exists(fig_path):
			fig_path += cls.ext
			assert os.path.exists(fig_path), fig_path+" does not exist."

		o,c,v = RPickle2.load(fig_path)
		assert float(v)>= 2

		dirpath,file_name=os.path.split(fig_path)

		filename,ext = os.path.splitext(file_name)


		sfig=RFigureCore(
				dict_variables=o[0],
				instructions=o[1],
				commentaries=c,
				globals_var=globals_var,
				filename   = filename   ,
				dirpath = dirpath ,
				)
		return sfig

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

	def formatName(self,filename=None,onlyExt=False,ext=None):
		"""
		Will format the filename
		"""
		if filename==None: filename=self.filename
		if ext==None: ext=self.ext
		if not onlyExt:
			if not re.match('^Figure_[0-9]{8}_',filename):
				filename = 'Figure_'+RDateDisplay.cur_date()+'_'+filename
		if not filename.endswith(ext):
			filename,_=os.path.splitext(filename)
			filename += ext
		self.filename = filename

		return filename
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
		- dirpath : the default place where we want to plot the file (default
			'.')
		- filename : the default name file.
		"""
		QtWidgets.QWidget.__init__(self,parent=parent)
		RFigureCore.__init__(self,*args,**kargs)
		self.setWindowTitle('RFigureGui 3 : Save matplotlib figure')



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
		actionSave	= QtWidgets.QAction("Save"		,self)
		actionClAll	= QtWidgets.QAction("Close All"	,self)
		actionSave.setShortcuts(QtGui.QKeySequence.Save)
		actionShow.setShortcuts(QtGui.QKeySequence("Ctrl+M"))
		actionShow.setShortcuts(QtGui.QKeySequence("Ctrl+Return"))
		self.addAction(actionShow)
		self.addAction(actionSave)

		button_show = QtWidgets.QPushButton('Show')
		button_save = QtWidgets.QPushButton('Save')
		button_addVar = QtWidgets.QPushButton('Add variable')
		button_clAll = QtWidgets.QPushButton('Close All')
		button_listVar = QtWidgets.QPushButton('Make list var')
		button_listVar = QtWidgets.QPushButton('Make list var')
		if self.globals_var==None:
			button_addVar.setEnabled(False)
			button_listVar.setEnabled(False)

		self.button_formatname = QtWidgets.QPushButton("Format Name")
		self.comboBox = QtWidgets.QComboBox()
		self.comboBox.addItems(self.fig_type_list+['None'])
		self.comboBox.setCurrentIndex(self.comboBox.findText('pdf'))
		self.lineEdit_dirpath	= QtWidgets.QLineEdit('./figures/')
		self.lineEdit_filename	= QtWidgets.QLineEdit()


		wid_line = QtWidgets.QWidget()
		wid_line.setSizePolicy( QtWidgets.QSizePolicy.Expanding,
			QtWidgets.QSizePolicy.Fixed)
		wid_layout = QtWidgets.QHBoxLayout()
		wid_layout.addWidget(QtWidgets.QLabel("Dir path:"))
		wid_layout.addWidget(self.lineEdit_dirpath)
		wid_layout.addWidget(QtWidgets.QLabel("File name:"))
		wid_layout.addWidget(self.lineEdit_filename)
		wid_layout.addWidget(self.button_formatname)
		wid_line.setLayout(wid_layout)



		splitter = QtWidgets.QSplitter(self)
		splitter.addWidget	(self.editor_python)
		splitter.addWidget	(wid_editor)
		lay = QtWidgets.QVBoxLayout()
		lay.addWidget(button_show )
		lay.addWidget(button_save )
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
		main_layout.addWidget(wid_line)
		wid = QtWidgets.QWidget()
		wid.setLayout(main_layout)



		self.setLayout(main_layout)

		button_show	  .clicked.connect(self.show)
		button_save	  .clicked.connect(self.save)
		button_clAll  .clicked.connect(self.closeAll)
		button_addVar .clicked.connect(self.table_variables.addItem)
		button_listVar.clicked.connect(self.make_list_variables)
		self.button_formatname.clicked.connect(self.formatName)
		actionShow 				.triggered.connect(self.show)
		actionSave 				.triggered.connect(self.save)
		actionClAll				.triggered.connect(self.closeAll)
		self.lineEdit_dirpath	.textChanged.connect(self.checkDirpath)

		QtWidgets.QWidget.show(self)
		self.uploadDataToGui()
		self.checkDirpath()



	def __del__(self):
		# Restore sys.stdout
		sys.stdout = sys.__stdout__

	def save(self):
		"""
		The saving function called by pushon the 'Save' button.
		Ask for confirmation and automotically asave the .png in the same time.
		"""
		self.instructions	=str(self.editor_python.toPlainText())

		self.commentaries	=str(self.editor_commentaries.toPlainText())
		self.dirpath		=str(self.lineEdit_dirpath.text())
		self.filename		= self.formatName(onlyExt=True)
		fig_type 			=str(self.comboBox.currentText())
		if fig_type=='None': fig_type=None

		if self.dirpath=="" : # by default it is in the current directory
			self.dirpath="."

		msg= "We are going to save the figure\n"+self.filename+\
			" in the directory "+self.dirpath
		msg = RTextWrap(str(msg))

		res = QtWidgets.QMessageBox.question ( self, "Saving confirmation",
			msg,QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)


		if (res == QtWidgets.QMessageBox.Yes):
			res = RFigureCore.save(self,dirpath=self.dirpath,filename=self.filename,
					fig_type=fig_type)
			if not res:
				msg = "The directory "+self.dirpath+" does not exist."
				QtWidgets.QMessageBox.information ( self, "No saving", msg)


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
			# # for frame in traceback.extract_tb(sys.exc_info()[2]):
			# 	# fname,lineno,fn,text = frame
			# 	# mess = "Error in %s on line %d" % (fname, lineno)
			# # line = sys.exc_traceback.tb_lineno

			# msgBox=QtWidgets.QMessageBox.critical(self,"Exec Error",
				# e.__class__.__name__+" : "+mess)
		finally:
			print("============ END ============")

	def closeAll(self):
		"""
		Slot that will close all the current matplotlib windows
		"""
		matplotlib.pyplot.close('all')

	@staticmethod
	def load(fig_path,globals_var=None):
		"""
		Static method used to load a figure from a .rfig file.
		"""
		sf = RFigureCore.load(fig_path)
		dirpath,filename=os.path.split(fig_path)

		return RFigureGui(dict_variables=sf.dict_variables,
								instructions=sf.instructions,
								commentaries=sf.commentaries,
								dirpath=dirpath,
								filename=filename,
								globals_var=globals_var
								)
	@staticmethod
	def loadFromRFigureCore(rfigcore,fig_path=None,globals_var=None):
		"""
		Static method used to upgrade a RFigureCore into a RFigureGui
		"""
		dirpath,filename=os.path.split(fig_path)

		return RFigureGui(dict_variables=rfigcore.dict_variables,
								instructions=rfigcore.instructions,
								commentaries=rfigcore.commentaries,
								dirpath=dirpath,
								filename=filename,
								globals_var=globals_var
								)



	def uploadDataToGui(self):
		self.table_variables.setRowCount(len(self.dict_variables))
		for i,k in enumerate(self.dict_variables.keys()):
			self.table_variables.setItem(i,0,QtWidgets.QTableWidgetItem(k))
		self.table_variables.updateFromDict()
		self.editor_python.setPlainText(self.instructions)
		self.editor_commentaries.setText(self.commentaries)
		self.lineEdit_filename.setText(self.filename)
		self.lineEdit_dirpath.setText(self.dirpath)


	def formatName(self,checked=False,filename=None,onlyExt=False):
		if filename==None:
			filename = str(self.lineEdit_filename.text())
		RFigureCore.formatName(self,filename=filename,onlyExt=onlyExt)
		self.lineEdit_filename.setText(self.filename)
		return self.filename

	def make_list_variables(self):
		self.instructions	=str(self.editor_python.text())
		ll = self.find_list_variables(in_globals_var=True)
		self.input_dict_from_list(ll)
		self.table_variables.updateFromDict()

	def closeEvent(self,event):
		matplotlib.pyplot.close('all')
		QtWidgets.QWidget.closeEvent(self,event)

	def outputWritten(self, text):
		"""Append text to the QTextEdit."""
		# Maybe QTextEdit.append() works as well, but this is how I do it:
		sys.__stdout__.write(text)
		cursor = self.editor_console.textCursor()
		cursor.movePosition(QtGui.QTextCursor.End)
		cursor.insertText(text)
		self.editor_console.setTextCursor(cursor)
		self.editor_console.ensureCursorVisible()

	def checkDirpath(self,text=None):
		dirpath = str(self.lineEdit_dirpath.text())
		palette = self.lineEdit_dirpath.palette()
		if os.path.exists(os.path.abspath(dirpath)):
			palette.setColor( QtGui.QPalette.Text, QtCore.Qt.green)
		else:
			palette.setColor( QtGui.QPalette.Text, QtCore.Qt.red)
		self.lineEdit_dirpath.setPalette(palette)

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



if __name__ == '__main__':
	iconpath = '/home/dessalles/.local/share/icons/hicolor/256x256/rfigure.ico'
	app.setWindowIcon(QtGui.QIcon(iconpath))

	sf=QtWidgets.QWidget()
	# def my_excepthook(type, value, tback):
	# 	res=type.__name__+":"+str(value)
	# 	if not (type.__name__=='SystemExit' and res=='SystemExit:0'):
	# 		msgBox=QtWidgets.QMessageBox.critical(sf, type.__name__, type.__name__+'\n'+res+'\n'+tback)
	# 	sys.__excepthook__(type, value, tback)
	# 	msgBox.show()
	if len(sys.argv)>1:
		f = ' '.join(sys.argv[1:])
		if f[-len(RFigureCore.ext):]== RFigureCore.ext:
			sf=RFigureGui.load(f)
		elif f[-len(RFigureCore.ext):]== '.rfig2':
			sf = convert_2_to_3(f,gui=True)
		else:
			print("ext",f[-len(RFigureCore.ext):])
			sf = convert_1_to_3(f,gui=True)
	else:
		sf=RFigureGui(instructions='',dict_variables={})
	# sys.excepthook = my_excepthook
	sys.exit(app.exec_())
