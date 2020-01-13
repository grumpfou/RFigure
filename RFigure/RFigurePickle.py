from __future__ import absolute_import, division, print_function,unicode_literals
import os,gzip
import subprocess
import random
from .RFigureMisc import decoDocFormating
# import numpy as np

__version__ = "2.1"

import sys
try:
    import numpy
    has_numpy = True
except ImportError:
    has_numpy = False

try:
    import pandas
    has_pandas = True
except ImportError:
    has_pandas = False


import sys
strings_types = [str]
if sys.version_info[0] < 3:
    pyth2=True
    strings_types.append(unicode)
else:
    pyth2=False
    unicode= str


###################### CONFIG IMPORTATION ##############################
path_to_header = './RFigureConfig/RFigureHeader.py'
file_dir = os.path.realpath(os.path.dirname(__file__))
path_to_header = os.path.join(file_dir,path_to_header)
########################################################################

authorized_types = [int,list,bool,dict,float,str,tuple]
if has_numpy:
    authorized_types += [numpy.ndarray,numpy.dtype]
    authorized_types += [numpy.int8,numpy.int16,numpy.int32,numpy.int64]
    authorized_types += [numpy.float16,numpy.float32,numpy.float64]
    authorized_types += [numpy.complex,numpy.complex64,numpy.complex128]
    authorized_types += [numpy.datetime64,numpy.timedelta64]

if has_pandas:
    authorized_types.append(pandas.core.frame.DataFrame)

def isAuthorized(v):
    """Function that determines if the object is authorised to be saved in a
    rpickle file. It checks recusivally (if a list or a dict) that the object
    can indeed be represented in a rpickle file.

    Parameters
    ----------
    v : any object
        the object to check

    Returns
    -------
    res : bool
        the status of the object
    """
    if type(v) in [list,tuple]:
        return all([isAuthorized(var) for var in v])
    elif has_numpy and type(v)==numpy.ndarray:
        return (v.dtype.type in authorized_types)
    elif has_pandas and type(v)==pandas.core.frame.DataFrame :
        return (v.dtype.type in authorized_types)
    else:
        return (type(v) in authorized_types)

def save(objects,filepath,commentaries="",version=None,ext='.rpk2'):
    """Function that will save the given objects in a rpickle file.

    Parameters
    ----------
    objects : list of dict
        the object to save (can be a list or a dict if needed).
    filepath : str
        the place where to save the sile, if has no extension, it will take the
        one of the class.
    commentaries : str
        string that contains commentaries about the thing
    version : str
        the version of the software that should use the pickle.
    ext : str
        the file extension (the dot should be included)
    """
    if version == None: version = __version__
    path,e = os.path.splitext(filepath)
    if len(e)==0:
        filepath+=ext
    imports = []
    to_save = object_to_txt([objects,commentaries,version],imports)
    to_save = '\n'.join(["import %s"%s for s in imports])+'\n'+to_save

    filepath_tmp = filepath+'__tmp__'+str(random.randint(0,10000)).zfill(4) # create a temporary file
    fid = gzip.GzipFile(filepath_tmp,'wb')

    try :
        fid.write(to_save.encode('utf-8'))
        print ("Pickle success")
    finally :
        fid.close()

    # if the file exists, we remove it, otherwise, error on Windows
    if os.path.exists(filepath):
        os.remove(filepath)

    os.rename(filepath_tmp,filepath)

@decoDocFormating(str(authorized_types))
def object_to_txt(objects,imports):
    """Function that will transform any object in its string version

    Parameters
    ----------
    objects : in %s
        the object to represent as a string
    imports : list of str
        list of all the libraries needed to define the object (will be updated
        insitus)

    Returns:
    res : str
        the string representation of the object

    """
    if type(objects) not in authorized_types:
        raise ValueError("The type "+str(type(objects))+" can not be save "+
            "using this pickle, only the ones in this list: "+str(authorized_types))
    res= u""
    if type(objects)==dict:
        res += "{"+",".join([object_to_txt(k,imports)+":"+object_to_txt(v,imports) for k,v in objects.items()]) + "}"

    elif type(objects)==tuple:
        res += "("+",".join([object_to_txt(o,imports) for o in objects]) + ")"
    elif type(objects)==list:
        res += "["+",".join([object_to_txt(o,imports) for o in objects]) + "]"
    elif has_numpy and type(objects)==numpy.ndarray:
        res += "numpy.array("+object_to_txt(list(objects),imports)+\
                    ',dtype=numpy.'+object_to_txt(objects.dtype,imports)+')'
        imports.append("numpy")

    elif has_pandas and type(objects)==pandas.core.frame.DataFrame:
        res += "pandas.DataFrame("+object_to_txt(objects.values,imports)+\
                    ",index = "+object_to_txt(list(objects.index),imports)+\
                    ",columns = "+object_to_txt(list(objects.columns),imports)+\
                    ")"
        imports.append("pandas")
    else:
        res += repr(objects)
    return res

def load(filepath):
    """ Load the RPickle file of filepath

    Parameters
    ---------
    filepath: path to the file to load

    Returns
    -------
    objets : list or dict
        the saved objects
    commentaries : str
        the commentaries stored in the file
    version : str
        the version string stored in the file
    """
    fid = gzip.GzipFile(filepath,'rb')
    try :
        reads = fid.read()
    finally :
        fid.close()

    fid = open (os.path.normpath(path_to_header),'r')
    try :
        if pyth2:
            instructions = unicode(fid.read().decode('utf-8'))
        else:
            instructions = fid.read()
    finally:
        fid.close()

    reads = reads.decode('utf-8').split('\n')
    instructions += '\n'+'\n'.join(reads[:-1])+"\n"+\
            'objects,commentaries,version = '+reads[-1]
    try:
        d=dict()
        exec(instructions,d)
        print("Success instructions")
    except BaseException as e:
        raise e
    return d['objects'],d['commentaries'],d['version']
