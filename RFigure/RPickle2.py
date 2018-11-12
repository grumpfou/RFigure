# PYTHON 3
# This script aims to replace RPickle which has some problems with the
# unicode in np.ndarray
from __future__ import absolute_import, division, print_function,unicode_literals
import numpy as np
import os,gzip
from . import  RPickle
import subprocess

__version__ = "2"

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


def save(objects,filepath,commentaries="",version=None,ext='rpk2'):
	"""
	- objects : the object to save (can be a list or a dict if needed).
	- filepath : the place where to save the sile, if has no extension,
		it will take the one of the class.
	- commentaries : string that contains commentaries about the thing
	- version : the version of the software that should use the pickle.
	- ext : the file extension
	"""
	if version == None: version = __version__
	path,e = os.path.splitext(filepath)
	if len(e)==0:
		filepath+='.'+ext
	to_save = object_to_txt([objects,commentaries,version])

	fid = gzip.GzipFile(filepath,'wb')
	try :
		fid.write(to_save.encode('utf-8'))
		print ("Pickle success")
	finally :
		fid.close()

def object_to_txt(objects):
	res= u""
	if type(objects)==dict:
		res += "{"+",".join([object_to_txt(k)+":"+object_to_txt(v) for k,v in objects.items()]) + "}"

	elif type(objects)==tuple:
		res += "("+",".join([object_to_txt(o) for o in objects]) + ")"
	elif type(objects)==list:
		res += "["+",".join([object_to_txt(o) for o in objects]) + "]"
	elif type(objects)==np.ndarray:
		res += "numpy.array("+object_to_txt(list(objects))+',dtype='+object_to_txt(objects.dtype)+')'


	# elif type(objects)==unicode:
	# 	res += repr(objects)

	else:
		res += repr(objects)
	return res


def load(filepath):
	""" Load the RPickle file of filepath
	- filepath: path to the file to load
	Returns:
	- objets, commentaries, version
	"""
	fid = gzip.GzipFile(filepath,'rb')
	try :
		reads = fid.read()
	finally :
		fid.close()

	fid = open (path_to_header,'r')
	try :
		if pyth2:
			instructions = unicode(fid.read().decode('utf-8'))
		else:
			instructions = fid.read()
	finally:
		fid.close()

	instructions += '\n'+'objects,commentaries,version = '+reads.decode('utf-8')
	try:
		d=dict()
		exec(instructions,d)
		print("Success instructions")
	except BaseException as e:
		raise e
	return d['objects'],d['commentaries'],d['version']


def convert_1_to_2(filepath,ext='.rpk2'):
	path,e = os.path.splitext(filepath)
	filepath1 = path+ext
	if sys.version_info[0] < 3:
		objects,commentaries,version = RPickle.load(filepath)
		save(objects,filepath1,commentaries,version)
	else:
		print("To call:", " ".join(["python2", __file__,filepath,ext]))
		res = subprocess.check_output(["python2", __file__,filepath,ext],stderr=subprocess.STDOUT)
		print("RPickle1 to RPickle2 success")
	return filepath1


if __name__=='__main__':
	if len(sys.argv)>1:
		convert_1_to_2(*sys.argv[1:])
