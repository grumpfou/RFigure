# PYTHON 3

import pickle
import os
import gzip

# def save(object, filename, bin = 1):
	# """Saves a compressed object to disk
	# """
	# file = gzip.GzipFile(filename, 'wb')
	# file.write(pickle.dumps(object, bin))
	# file.close()

__version__ = "0_python3"


def save(objects,filepath,commentaries=None,version=None,ext='rpy'):
	"""
	- objects : the object to save (can be a list or a dict if needed).
	- filepath : the place where to save the sile, if has no extension,
		it will take the one of the class.
	- commentaries : string that contains commentaries about the thing
	- version : the version of the software that should use the pickle.
	"""
	if version == None: version = __version__
	if commentaries==None:
		commentaries=""

	path,e = os.path.splitext(filepath)
	if len(e)==0:
		filepath+='.'+ext
	fid = gzip.GzipFile(filepath,'wb')
	buffer = ""
	try :
		pickle.dump(objects,fid,protocol=2)
		pickle.dump(commentaries,fid,protocol=2)
		pickle.dump(version,fid,protocol=2)
		print ("Pickle success")
	finally :
		fid.close()

def load(filepath):
	fid = gzip.GzipFile(filepath,'rb')
	try :
		objects = pickle.load(fid)
		commentaries = pickle.load(fid)
		version = pickle.load(fid)
	except UnicodeDecodeError as e:
		print ("e : ",e)
		try : #2 to 3
			def get():

				u = pickle._Unpickler(fid)
				u.encoding = 'latin1'
				return u.load()
			objects = get()
			commentaries = get()
			version = get()
			# objects = pickle.load(fid)
			# commentaries = pickle.load(fid)
			# version = pickle.load(fid)
		finally :
			fid.close()
	finally :
		fid.close()


	return objects,commentaries,version
