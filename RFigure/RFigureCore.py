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
from . import RFigurePickle
from .RFigureMisc import RDateDisplay, RTextWrap
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
        >                                                   # with the pdf file
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

        RFigurePickle.save(objects,filepath,self.commentaries,version = __version__)
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
        o,c,v = RFigurePickle.load(filepath)
        assert v>= "2"

        self.commentaries = c
        self.instructions = o[1]
        self.globals_var = globals_var
        self.dict_variables = o[0]
        self.filepath = filepath


    @classmethod
    def load(cls,filepath,globals_var=None):
        """Return a RFigureCore instance"""
        sfig=cls()
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

if __name__ == '__main__':
    from . import RFigureGui
    RFigureGui.main(sys.argv)
