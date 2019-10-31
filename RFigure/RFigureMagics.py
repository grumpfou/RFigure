from . import RFigureCore
from . import RFigurePickle
import os,re,sys,argparse,shlex,textwrap
import numpy as np
from IPython.core.magic import  (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
def find_list_variables(instructions,locals_):
    """Try ot find the names of  variables that are used in the instructions.

    Parameters
    ----------
    instructions : str
        the instructions in which we find the variables
    locals_ : dict
        the dict in whhich should be the variables


    Returns
    -------
    vars_ : list of str
        list of all the name of the variables used in the instructions
    """
    # Remove commentaries
    # NOTE: will also remove something like a="# this is not a comment" # this is a comment
    lines = [line.split('#')[0] for line in instructions.split("\n")]
    instructions = '\n'.join(lines)
    # remove assignments
    instructions = re.sub(r'\b\w+\b *=',"",instructions)

    # we search the all the words
    vars_ = re.findall(r'\b\w+\b',instructions)
    vars_ = list(set(vars_))

    # we remove the varibales of the for loops if they are not used before in the instructions
    # for res in re.finditer(r'\s*for +\b([\w ,]+)\b +\bin\b',instructions):
    for res in re.finditer(r'\s*for (.*)\bin\b',instructions):
        pos = res.start()
        vars_string = res.groups()[0].strip()

        # to deal with example lifke "for i,(x,y) in enumerate(.....)"
        vars_string = vars_string.replace('(','')
        vars_string = vars_string.replace(')','')

        # example: "for x, y in range(10)" → var_list=['x','y']
        var_list = [r.strip() for r in vars_string.split(',')]
        l_filter = lambda r: (not (re.match('(\w)+',r)  is None)) and (re.match('(\w)+',r).group()==r)
        var_list = list(filter(l_filter,var_list))

        for v in var_list:
            try:
                pos1 = re.search(r'\b%s\b'%v,instructions).start()

                # if the first iterance of `v` is at the for loop,
                if pos1>=pos and v in vars_:
                    # we remove `v` from `vars_`
                    vars_.remove(v)
            except:
                print('Problem with the regular expression: \'%s\''%v)

    # we filter all the variables that are in locals_
    vars_ = [a for a in vars_ if a in locals_]
    # we filter all the variables that can be saved in RFigurePickle
    vars_ = filter(lambda x : RFigurePickle.isAuthorized(locals_[x]),vars_)
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



class MyArgumentParser(argparse.ArgumentParser):
    class ArgumentParserError(Exception): pass
    def error(self, message):
        raise self.ArgumentParserError(message)
    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, _sys.stderr)


@magics_class
class RFigureMagics(Magics):
    epilog_save = """
                Examples
                --------
                (in IPython/Jupyter)

                >>> import numpy as np
                ... a = np.arange(0,10,.1)
                ... b = np.cos(a)
                ... comment = "A comment"
                ... diction = {'a':a,'b':1/a}

                >>> %%rfig_save Test
                ... # search the variables in the instructions, no comment and save in pdf
                ... plt.plot(a,b)

                >>> %%rfig_save -c comment Test
                ... # search the variables in the instructions, with a comment and save in pdf
                ... plt.plot(a,b)

                >>> %%rfig_save --fig_type png Test
                ... # search the variables in the instructions, no comment and save in png
                ... plt.plot(a,b)

                >>> %%rfig_save -d diction Test
                >>> # specify other variables, no comment, save in pdf
                >>> plt.plot(a,b)

                >>> %%rfig_save --format_name Test
                ... # search the variables in the instructions, format the filename
                ... plt.plot(a,b)
                """

    parser_save = MyArgumentParser(
        prog='%%rfig_save',
        description = ("Will save a RFigure, whose instructions are the "
                            "code written in the remaining of the cell."),
        add_help=False,epilog=textwrap.dedent(epilog_save),
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser_save.add_argument("--help","-h",
        help="show this help message and exit",
        action="store_true")

    parser_save.add_argument("--format_name","-fn",
        help=("Format the name of the file as Figure_YYYYMMDD_foo where "
              "YYYYMMDD stands for the date. `foo` will be the file names. "
              "If the file name is already under this format, do notiong."),
      action="store_true")

    parser_save.add_argument("-d",
        help="Dictionary of the locals in the rfigure file. If not "
             "specified, guess from the instructions.",
        nargs=1)

    parser_save.add_argument("-c",
        help="Comments associated to the file",
        nargs=1)

    parser_save.add_argument("--fig_type",'-ft',
        help="extension of the figure, should be in "+str(RFigureCore.fig_type_list),
        nargs=1)

    parser_save.add_argument("filepath",
        help="Path of the file.",
        nargs='?')

    @cell_magic
    def rfig_save(self,line,cell):
        args = self.parser_save.parse_args(shlex.split(line))
        if args.help:
            self.parser_save.print_help()
            return True
        if args.filepath is None:
            self.parser_save.error("the following arguments are required: filepath")
        if args.d is None:
            args.d = find_vars_dict(cell)
            print("We determined the RFigure variables to be: `"+"`, `".join(args.d.keys())+"`")
        else:
            args.d = eval(args.d[0],find_ipython_locals())
        if args.c is None:
            args.c = ""
        else:
            args.c = eval(args.c[0],find_ipython_locals())
        if args.fig_type is None:
            args.fig_type = 'pdf'
        elif args.fig_type=='None':
            args.fig_type = None
        else:
            args.fig_type = args.fig_type[0]

        cell = cell.strip()
        if cell.startswith("%pylab"):
            # if the first line is a pylab magic, remove the first line
            cell = '\n'.join(cell.split('\n')[1:])

        rf = RFigureCore(d=args.d,i=cell,c=args.c,filepath=args.filepath)
        if args.format_name:
            rf.formatName()
        rf.save(fig_type=args.fig_type)
    rfig_save.__doc__ = parser_save.format_help()


    epilog_list_var = """
                Examples (in IPython/Jupyter):

                In[1]:
                > a = np.arange(0,10,.1)
                > b = np.cos(a)

                In[2]:
                > %%rfig_list_var
                > plot(a,b)
                We determined the RFigure variables to be: `a`, `b`

                In[3]:
                > %%rfig_list_var a_dict
                > plot(a,b)
                We determined the RFigure variables to be: `a`, `b`

                In[4]:
                > print(a_dict.keys())
                dict_keys(['a','b'])
                """
    parser_list_var = MyArgumentParser(
        prog='%%rfig_list_var',
        description = ("Detects the variables in the code of the cell."),
        add_help=False,epilog=textwrap.dedent(epilog_list_var),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser_list_var.add_argument("--help","-h",
        help="show this help message and exit",
        action="store_true")
    parser_list_var.add_argument("dict_variable",
        help="the variable name of the dictionary in which will be stored the "
                "variables detected in the cell. If none is given, only prints "
                "its keys.",
        nargs='?')
    @cell_magic
    def rfig_list_var(self,line,cell):
        args = self.parser_list_var.parse_args(shlex.split(line))
        if args.help is True:
            self.parser_list_var.print_help()
            return True
        d = find_vars_dict(cell)
        print("We determined the RFigure variables to be: `"+"`, `".join(d.keys())+"`")
        if not args.dict_variable is None:
            print("args.dict_variable[0]",args.dict_variable)
            self.shell.user_ns.update({args.dict_variable:d})
    rfig_list_var.__doc__ = parser_list_var.format_help()

    epilog_load = ""
    """
                Examples (in IPython/Jupyter):

                In[1]:
                > # Opens the RFigure Test.rfig3:
                > # 1) import its variables in the notebook locals
                > # 2) checks that %pylab is imported (if not addd it)
                > # 3) create a new cell with the instructions
                > %rfig_load "Test.rfig3"

                In[2]:
                > # Opens the RFigure Test.rfig3:
                > # 1) stores the variables in `ddd`
                > # 2) stores the instructions in `iii`
                > # 3) stores the commentaries in `ccc`
                > %rfig_load -i iii -c ccc -d ddd "Test.rfig3"
                """
    parser_load = MyArgumentParser(
        prog='%%rfig_load',
        description = ("Will load a RFigure in the Jupyter notebook."),
        add_help=False,epilog=textwrap.dedent(epilog_load),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser_load.add_argument("--help","-h",
        help="show this help message and exit",
        action="store_true")
    parser_load.add_argument('-d',
        help="the variable name of the dictionary in which will be stored the "
            "variables of the RFigure. If none is given, import in the "
            "notebook locals.",
        nargs=1)
    parser_load.add_argument('-i',
        help="the variable name of the string in which will be stored the "
            "instructions of the RFigure. If none is given, create a new cell "
            "filled with the instructions. Also checks if the magic `%%pylab` "
            "has been executed. If not, it adds the command `%%pylab` at the "
            "begining of the instructions",
        nargs=1)
    parser_load.add_argument('-c',
        help="the variable name of the string in which will be stored the "
            "commentaries of the RFigure.",
        nargs=1)
    parser_load.add_argument("filepath",
        help="Path of the file to open.",
        nargs='?')
    @line_magic
    def rfig_load(self,line):
        """ Magic function to open an existing rfigure and import the
        instructions and update the locals with the rfigure variables.
        """

        args = self.parser_load.parse_args(shlex.split(line))
        if args.help:
            self.parser_load.print_help()
            return True
        if args.filepath is None:
            self.parser_load.error("the following arguments are required: filepath")

        rf = RFigureCore.load(args.filepath)
        if args.d is None:
            self.shell.user_ns.update(rf.dict_variables)
        else:
            self.shell.user_ns.update({args.d:rf.dict_variables})


        raw_code = rf.instructions
        if not all([mod in sys.modules for mod in
                ["numpy","matplotlib","figsize","plt","pylab" "mlab", "pyplot"]
                ]):
            #Heuristic to know if the magics %pylab has been alredy exectued
            raw_code = "%pylab\n"+raw_code

        if args.i is None:
            self.shell.set_next_input('{}'.format(raw_code))
        else:
            self.shell.user_ns.update({args.i[0]:raw_code})

        if not args.c is None:
            self.shell.user_ns.update({args.c[0]: rf.commentaries})
        # self.shell.user_ns.update(...)
    rfig_load.__doc__ = parser_load.format_help()

    @line_magic
    def rfig_curdate(self,line):
        """ Magic function that assign a different current date that will be
        used when formating the names.

        Examples (in IPython/Jupyter):

        >>> %rfig_save --format_name Test
        ... # Will save in the file `Figure_YYYYMMDD_Test.rfig3` where YYYYMMDD
        ... # stands for the current date.
        ... plt.plot(np.arange(10),np.arange(10))

        >>> %rfig_crudate 19990909

        >>> %rfig_save --format_name Test
        ... # Will save in the file `Figure_19990909_Test.rfig3` whenever
        ... plt.plot(np.arange(10),np.arange(10))
        """
        RFigureCore.CURDATE = line.strip()

def load_ipython_extension(ipython):
    ipython.register_magics(RFigureMagics)
