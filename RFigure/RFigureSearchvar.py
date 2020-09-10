
from . import RFigurePickle
import re,sys, linecache

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

                # if the first occurence of `v` is at a for loop,
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


def find_obj_name(list_obj,frame=1):
    '''Function that returns the names of the objects contained in `list_obj`.

    Parameters
    ----------
    list_obj : list of objects
        the object to finf the name of
    frame : int or str
        which frame  should it consider
        if int: how much frames go back to find the name of the objects
        if str: what name of a function should we find to stop the search

    Returns
    -------
    names: list
        - if we determine a unique name for the i-th element, then `names[i]`
            is the name of the i-th element
        - if we determine several possible names for the i-th element, then
            `names[i]` is the list of these possible names
        - if we could not determine any possible names for the i-th element,
            then `names[i]==None`
    '''
    if type(frame)==int:
        f = sys._getframe(frame)
    elif type(frame)==str:
        i = 0
        while True:
            try:
                f = sys._getframe(i)
            except ValueError:
                raise StopIteration('Could not find the ipython instance in all the frames')
            if frame in f.f_code.co_names:
                break
            i+=1
    else:
        raise ValueError("The variable `frame` should be either an int or a str")
    linecall = linecache.getlines(f.f_code.co_filename)[f.f_lineno-1] # why -1 ? don't know
    locals_ = f.f_locals
    result = []
    for a in list_obj:
        list_locals = [k for k,v in locals_.items() if v==a]
        if len(list_locals)==0:
            result.append(None)
        elif len(list_locals)==1:
            result.append(list_locals[0])
        else:
            vars_ = re.findall(r'\b\w+\b',linecall)
            vars_ = list(set(vars_))
            list_locals_new = [k for k in list_locals if k in vars_]
            if len(list_locals_new)==0:
                result.append(None)
            elif len(list_locals_new)==1:
                result.append(list_locals_new[0])
            else:
                result.append(list_locals_new)
    return result

def find_varsdict_from_cell(cell):
    ipy_locals = find_ipython_locals()
    vars_ = find_list_variables(instructions=cell,locals_=ipy_locals)
    d = {k:ipy_locals[k] for k in vars_}
    return d

def find_varsdict_from_list(list_obj):
    list_name = find_obj_name(list_obj)
    res = dict()
    for i,k in enumerate(list_name):
        if k is None:
            print('CAUTION: could not determine the name for the %i-th object'%i)
        elif type(k)==list:
            for kk in k:
                res[kk] = list_obj[i]
        else:
            res[k] = list_obj[i]
