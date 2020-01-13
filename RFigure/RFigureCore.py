# PYTHON 3
""" Unless mentionned otherwise, the code is written by R. Dessalles (Grumpfou).
Published under license GNU General Public License v3.0. Part of the RFigure
project.
"""
import matplotlib
import warnings
import inspect
import textwrap

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
from .RFigureMisc import RDateDisplay, RTextWrap,decoDocFormating
from matplotlib.backends.backend_pdf import PdfPages

__version__ = '3'

###################### CONFIG IMPORTATION ##############################
path_to_header = './RFigureConfig/RFigureHeader.py'
file_dir = os.path.realpath(os.path.dirname(__file__))
path_to_header = os.path.join(file_dir,path_to_header)
########################################################################

# matplotlib.pyplot.ion()


class RFigureCore:
    """
    This si the RFigureCore core class.
    """
    CURDATE = None # you can reassign CURDATE to the date by default (something like `'20191031'` )
    ext = '.rfig3'
    fig_type_list=['pdf','eps','png','svg']
    def __init__(self,
            d=None,i=None,c=None,
            file_split="# RFIG_start_instructions",
            filepath=None):
        """
        This function will save the figure into a propper way, in order to open
        it again.

        Parameters
        ----------
        d : dict
            dictionary that contain the variable useful to plot the figure.
        i : str or func
            instructions, string that contains the python code to create the
            figure. If it is a function, takes the source of the function.
        c : str
            commentaries where the user can describe the figure.
        file_split : str
            file_split it the string that will separate the instructions. What
            will be bollow the first instance of will be considered as the
            instructions. If `file_split` string is not encountered, keeps the
            whole instructions
        filepath : str
            the path to the file (useful for the local header and to directly
            save the file)

        Example
        -------
        >>> import RFigure,numpy
        ... X = numpy.arange(0,10,0.1)
        ... Y = numpy.cos(X)
        ... i = "plot(X,Y)" # the instrucutions
        ... d = dict(X=X,Y=Y) # the data to display
        ... c = "This is a test" # the commentaries associate with the figures
        ... rf = RFigure.RFigureCore(d=d,i=i,c=c)
        ... rf.show() # execute the instructions to be sure it works
        ... rf.save(filepath='./Test.rfig3') # only save the rfig3 file
        ... rf.save(filepath='./Test.rfig3',fig_type='pdf') # save the rfig3 file as well as the pdf associated
        """
        if i is None:
            self.instructions = ""
        elif callable(i):
            self.instructions = textwrap.dedent(
                                '\n'.join(inspect.getsource(i).split('\n')[1:]))
        else:
            self.instructions = i
        self.commentaries = "" if c is None else c
        self.dict_variables = {} if d is None else d
        self.file_split = file_split

        self.clean_instructions() # we clean the instructions

        self.filepath = filepath

        assert type(self.instructions) is str
        assert type(self.commentaries) is str
        assert type(self.dict_variables) is dict
        assert type(self.file_split) is str

    def execute(self,print_errors=False):
        """
        The method executes the instructions (no `show` at the end). Proceed in
        four steps:
        1. executes the general header file `RFigure/RFigureConfig/RFigureHeader.py`
        2. executes the local header file `./.RFigureHeaderLocal.py`
        3. updates the locals with the rfig variables `self.dict_variables`
        4. executes the rfig instructions `self.instructions`

        Parameters
        ----------
        print_errors : bool
            if True, will print the errors rather than raise them (to avoid
            some troubles with PyQt5)
        """
        if self.filepath!=None:
            dirpath,_ = os.path.split(self.filepath)
        else:
            dirpath = '.'
        matplotlib.pyplot.close('all')
        if os.path.exists(path_to_header):
            with  open (path_to_header,'r') as fid:
                instructions_header_general = fid.read()
        else:
            print("Could not find the path to header")
            instructions_header_general = ""

        if not dirpath is None:
            path_to_header_local = os.path.join(dirpath,'./.RFigureHeaderLocal.py')
        if os.path.exists(path_to_header_local):
            with open (path_to_header_local,'r') as fid:
                instructions_header_local = fid.read()
        else:
            instructions_header_local = ""

        dict_variables = dict()
        def exec_instructions(instructions,filename,globals_):
            locals_ = {}
            try:
                code = compile(instructions,filename,'exec')
                exec(code,globals_,**locals_)
                globals_.update(locals_)
            except Exception as e :
                if print_errors:
                    traceback.print_exc()
                    return False
                else:
                    raise e
            return locals_

        # locals_ = {}
        globals_ = {}
        exec_instructions(instructions_header_general,path_to_header,globals_)
        exec_instructions(instructions_header_local,path_to_header_local,globals_)
        globals_.update(self.dict_variables.copy())
        exec_instructions(self.instructions,'RFigureInstructions',globals_)
        return globals_

    def show(self,print_errors=False):
        """ Method that execute the code instructions and adds the
        matplotlib.pyplot.show() statement at the end.

        Parameters
        ----------
        print_errors : bool
            if True will print the errors rather than raise them (to avoid
            some troubles with PyQt5)
        """
        self.execute(print_errors=print_errors)
        matplotlib.pyplot.show()

    @decoDocFormating(fig_type_list)
    def save(self,filepath=None,fig_type=None,check_ext=True):
        """
        Will save the figure in a rfig file.

        Parameters
        ----------
        filepath : str
            The filepath where to save the figure. Adds the extension if
            necessary. If None, search the attribute self.filepath (if
            self.filepath also None, raise an error). Is not None, set
            `self.filepath` to the new file path.
        fig_type : None, str or list(str)
            if not None, will save the figure in the corresponding format (if it
             is a list, will save in several formats). Should be in %s.
        check_ext: bool
            if True, adds if necessary the extension to filepath

        Returns
        -------
        paths : list of str
            the paths of the files created/edited (i.e. the rfig file and the
            pdf/png/etc. that represents the figure)
        """
        if filepath is None:
            filepath = self.filepath
        if filepath is None:
            raise TypeError("The `filepath` needs to be specified")


        objects = [self.dict_variables,self.instructions]

        RFigurePickle.save(objects,filepath,self.commentaries,
            version = __version__,ext=self.ext)
        paths = [filepath]
        if fig_type:
            paths1 = self.savefig(filepath,fig_type=fig_type)
            paths += paths1
        self.filepath = filepath
        return paths

    @decoDocFormating(fig_type_list)
    def savefig(self,fig_path,fig_type='png'):
        """Method that will save the figure with the corresponding extention.

        Parameters
        ----------
        fig_path : str
            The path of where to save the figure the figure.
        fig_type :  None, str or list(str)
            if not None, will save the figure in the corresponding format (if it
             is a list, will save in several formats). Should be in %s.

        Returns
        -------
        paths : list of str
            the paths of the files created/edited (i.e. the rfig file and the
            pdf/png/etc. that represents the figure)
        """
        if type(fig_type)==list:
            paths = []
            for ext in fig_type:
                paths += self.savefig(fig_path=fig_path, fig_type=ext)
            return paths

        assert fig_type in self.fig_type_list

        dirpath,_=os.path.split(fig_path)
        if fig_type not in self.fig_type_list and not (fig_type is None):
            raise ValueError('fig_type should be in '+str(self.fig_type_list))
        matplotlib.pyplot.ion()

        globals_ = self.execute()

        # `RFIG_savefig_kargs` is a dict that contains the possible kargs to
        # add when using `matplotlib.figure.Figure.savefig(...,**kargs)`
        if 'RFIG_savefig_kargs' in globals_:
            RFIG_savefig_kargs = globals_['RFIG_savefig_kargs']
        else:
            RFIG_savefig_kargs = dict()

        # we make the list of all the figures
        figures=[manager.canvas.figure for manager in \
                    matplotlib._pylab_helpers.Gcf.get_all_fig_managers()]

        paths = []
        if fig_type in {'png','eps','svg'}:
            fig_path,_ = os.path.splitext(fig_path)

            # if there is more than one figure, we will save under the names :
            # Sometitle_00.png , Sometitle_01.png, Sometitle_02.png
            if len(figures)>1:
                to_zfill=np.log10(len(figures))+1
                for i,fig in enumerate(figures):
                    nb='_'+str(i).zfill(int(to_zfill))
                    f = fig_path+nb+'.'+fig_type
                    fig.savefig(f,bbox_inches='tight',**RFIG_savefig_kargs)
                    paths.append(f)
            elif len(figures)>0:
                f = fig_path+'.'+fig_type
                figures[0].savefig(fig_path+'.'+fig_type,bbox_inches='tight',
                                                        **RFIG_savefig_kargs)
                paths.append(f)
        elif fig_type=='pdf':
            fig_path,_ = os.path.splitext(fig_path)
            fig_path += '.'+fig_type
            pp = PdfPages(fig_path)
            for fig in figures:
                # pp.savefig(fig,bbox_inches='tight',transparent=True)
                pp.savefig(fig,bbox_inches='tight',**RFIG_savefig_kargs)
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




    def open(self,filepath):
        """Open the rfig file from filepath

        Parameters
        ----------
        filepath : str
            the path of the rfigure. Set the attribute self.filepath to this
            value
        """
        if not os.path.exists(filepath):
            filepath += self.ext
            assert os.path.exists(filepath), filepath+" does not exist."
        o,c,v = RFigurePickle.load(filepath)
        assert v>= "2"

        self.commentaries = c
        self.instructions = o[1]
        self.dict_variables = o[0]
        self.filepath = filepath


    @classmethod
    def load(cls,filepath):
        """Return a RFigureCore instance that had openned the rfigure.

        Parameters
        ----------
        filepath : str
            the path of the rfigure to load

        Returns
        -------
        rfig : RFigureCore
            The RFigureCore instance created.
        """
        rfig=cls()
        rfig.open(filepath)
        return rfig

    @staticmethod
    def update(fig_path,d=None,i=None,c=None,mode='append',fig_type=None):
        """
        Update the dict_variables of an already existing file:

        Parameters
        ----------
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


        Returns
        -------
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

    def formatName(self,filepath=None,replace_current=True):
        """
        Format the filename under the format: "path/Figure_YYYYMMDD_foo.rfig3"
        where foo is the current filename. If the filpath is already under this
        format, do not change it. It updates the attribute `self.filepath`.

        Parameters
        ----------
        filepath : str
            the filepath to format, by default takes `self.filename`
        replace_current : bool
            if True, then replace the current `self.filepath` by the one
            obtained

        Returns
        -------
        filepath : str
            the new filepath with the updated file name

        Example
        -------
        >>> rf = RFigureCore(filpath='./foo/faa.rfig3')
        >>> rf.formatName()
        "./foo/Figure_20181201_faa.rfig3"
        >>> rf.formatName(filepath='./foo/fii.rfig3')
        "./foo/Figure_20181201_fii.rfig3"
        >>> rf.formatName(filepath='./foo/Figure_20181201_fuu.rfig3')
        "./foo/Figure_20181201_fuu.rfig3"

        (with each time, 20181201 corresponding to the curent date)
        """
        if filepath is None:
            filepath = self.filepath
        dirpath,filename = os.path.split(filepath)
        if not re.match('^Figure_[0-9]{8}_',filename):
            if self.CURDATE is None:
                filename = 'Figure_'+RDateDisplay.cur_date()+'_'+filename
            else:
                assert  re.match('^[0-9]{8}$',self.CURDATE)
                filename = 'Figure_'+self.CURDATE+'_'+filename
        filepath = os.path.join(dirpath,filename)
        if replace_current: self.filepath = filepath
        return filepath

    def formatExt(self,filepath=None,ext=None,replace_current=True):
        """
        Changes/adds if necessary the extension to the filepath. Update the
        attribute `self.filepath` accordingly

        Parameters
        ----------
        filepath : str
            the filepath to format.
        ext :  str
            the extension (the dot needs to be included). By default, takes
            `self.ext`.
        replace_current : bool
            if True, then replace the current `self.filepath` by the one
            obtained

        Returns
        -------
        filepath : str
            the new filepath with the updated file extension
        """
        if ext==None: ext=self.ext
        dirpath,filename = os.path.split(filepath)
        if not filename.endswith(ext):
            filename,_=os.path.splitext(filename)
            filename += ext

        filepath = os.path.join(dirpath,filename)
        if replace_current: self.filepath = filepath
        return filepath


if __name__ == '__main__':
    from . import RFigureGui
    RFigureGui.main(sys.argv)
