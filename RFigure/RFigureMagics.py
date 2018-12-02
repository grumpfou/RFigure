from . import RFigureCore
import os,re,sys
import numpy as np
from IPython.core.magic import  (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
def find_list_variables(instructions,locals_):
    vars_ = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',instructions)
    vars_ = list(set(vars_))
    vars_ = [a for a in vars_ if a in locals_]
    vars_ = [a for a in vars_ if type(locals_[a]) in {np.ndarray,list,int,float,str,bool}]
    return vars_

def find_ipython_locals():
    i=0
    while True:
        try:
            f = sys._getframe(i)
        except ValueError:
            raise StopIteration('Could not find the ipython instance in all the frames')
        if f.f_code.co_filename.startswith("<ipython"):
            ipy_locals = f.f_locals
            break
        i+= 1
    return ipy_locals

def find_vars_dict(cell):
    ipy_locals = find_ipython_locals()
    vars_ = find_list_variables(instructions=cell,locals_=ipy_locals)
    d = {k:ipy_locals[k] for k in vars_}
    return d

@magics_class
class RFigureMagics(Magics):
    @cell_magic
    def rfig_save(self,line, cell):
        """ Will save a RFigure, whose instructions are the the code written in the
        remaining of the cell.

        Usage:
        In[]:
        > %%rfig filepath [, dict_variables [, comments [, fig_type]]]
        > # RFigure instructions (code to create the file)

        Parameters:
        - filepath: str
            the path of the file
        - dict_variables: dict or None
            the dictionary that contain the variables of teh RFigure. If not
            specified or None, will guess them from the the instructions.
        - comments: st
            the commentraries of teh RFigure, by default, empty string
        - fig_type: str in RFigure.RFigureCore.fig_type_list
            the extention of the figure (if nothing ot None, it takes the "pdf" by
            default)

        The rest of the cell will represent the instructions to save in the RFigure.

        Examples (in IPython/Jupyter):

        In[1]:
        > a = np.arange(0,10,.1)
        > b = np.cos(a)

        In[2]:
        > %%rfig_save "Test"
        > # search the variables in the instructions, no comment and save in pdf
        > plt.plot(a,b)

        In[3]:
        > %%rfig_save "Test",None,"This is a comment"
        > # search the variables in the instructions, with a comment and save in pdf
        > plt.plot(a,b)

        In[4]:
        > %%rfig_save "Test",None,None, 'png'
        > # search the variables in the instructions, no comment and save in png
        > plt.plot(a,b)

        In[5]:
        > %%rfig_save "Test",{"a":np.arange(-1,1,.1),"b":1/np.arange(-1,1,.1)}
        > # specify other variables, no coment, save in pdf
        > plt.plot(a,b)
        """


        if line.strip()=="":
            raise ValueError('Specify the RFigure file name.')
        line = eval(line,find_ipython_locals())
        if not type(line)==tuple or type(line)==list:
            line = (line,)

        # 1st element: filepath
        if len(line)<1 or (line[0] is None):
            raise ValueError('Specify the RFigure file name.')
        else:
            filepath = line[0]
            if type(filepath)!= str:
                raise TypeError("The name of the file should be a string")
            if os.path.splitext(filepath)[1]=='':
                filepath+='.rfig3'

        # 2nd element: RFigure variable dictionary
        if len(line)<2 or (line[1] is None):
             # We search in sys._getframe the one corresponding to the ipython instance

            d = find_vars_dict(cell)
            print("We determined the RFigure variables to be: `"+"`, `".join(d.keys())+"`")

        else:
            d = line[1]
            if type(d)!= dict:
                raise TypeError("The RFigure variables should be either None or a dictionary")

        # 3rd element: the commentaries
        if len(line)<3 or (line[2] is None):
            c = ""
        else:
            c = line[2]
            if type(c)!= str:
                raise TypeError("The RFigure comments should be a string")

        # 4th element: the fig_type
        if len(line)<4 or (line[3] is None):
            fig_type = "pdf"
        else:
            fig_type = line[3]
            if type(fig_type)!= str or (fig_type not in RFigure.RFigureCore.fig_type_list):
                raise TypeError("The RFigure fig_type should be in "+
                                        str(RFigure.RFigureCore.fig_type_list))


        rf = RFigure.RFigureCore(d=d,i=cell,c=c)
        rf.save(filepath=str(filepath),fig_type=fig_type)

def load_ipython_extension(ipython):
    ipython.register_magics(RFigureMagics)
