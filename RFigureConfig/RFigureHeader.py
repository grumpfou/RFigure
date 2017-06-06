##### Header : ####
# This part is usefull if the variable 'e' is used in the globals because
# otherwise it would be erased by the constant numpy.e
if 'e' in globals().keys():
	__tmp_e__ = globals()['e']
	__is__tmp_e__ = True
else:
	__is__tmp_e__ = False

import matplotlib
matplotlib.rcParams.update({'font.size': 20})

from numpy import *
import numpy as np
import numpy
from matplotlib.pyplot import *
import matplotlib._pylab_helpers
import matplotlib.pyplot as plt

if __is__tmp_e__ == True :
	e = __tmp_e__

##### Script : ####
