##### Header : ####
# This part is usefull if the variable 'e' is used in the globals because
# otherwise it would be erased by the constant numpy.e

__tmp_dict__ = dict()
__list_protected__ = {'e','pi'}
for  var in __list_protected__:

	if var in globals().keys():
		__tmp_dict__[var] = globals()[var]

import matplotlib
matplotlib.rcParams.update({'font.size': 20})
matplotlib.rcParams.update({'text.latex.preamble': r'\usepackage{amsfonts}'})

from numpy import *
import numpy as np
import numpy
from matplotlib.pyplot import *
import matplotlib._pylab_helpers
import matplotlib.pyplot as plt

if len(__tmp_dict__)>0 :
	globals().update(__tmp_dict__)

##### Script : ####
