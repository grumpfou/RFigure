# PYTHON 3
import datetime,re
import textwrap
import numpy as np
import subprocess
class RDateDisplay:
	"""Methods to display the string that represent the date.
	"""
	@staticmethod
	def cur_date(date="Today",with_hour=False):
		""" Will return a string containing the date under the format YYYYMMDD
		date : in [""Today", "Yesterday, "Tomorrow"] (dft "Today"). we represent
			which day
		with_hour : If True return add the hours to the string. The format will
			then be YYYYMMDDHHMMSS.
		"""
		dico={
				"Today" 	: 0  ,
				"Yesterday" : -1 ,
				"Tomorrow" 	: 1  ,
			}
		now=datetime.datetime.now()
		if date in dico.keys():
			date=now+datetime.timedelta(dico[date])
		if type(date)==int:
			date=now+datetime.timedelta(date)
		if with_hour:
			return date.strftime("%Y%m%d%H%M%S")
		else:
			return date.strftime("%Y%m%d")
	@staticmethod
	def date_from_str(s):
		"""Will return the datetime corresponding to the s whise format is
		YYYYMMDD"""
		assert re.match('[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]',s)
		d = datetime.date(int(s[0:4]), int(s[4:6]), int(s[6:8]))
		return d


def RTextWrap(text,nb=79,sep='\n',begin="") :
	"""Will return the text properly wrapped
	text : the textg to wrap
	nb : the limit at which we wrap the text
	sep : the char that seperate the paragraphs
	begin : the char that should begin each line
	"""
	l = text.split(sep)
	ll = [textwrap.fill(f.strip(),nb-len(begin),
		initial_indent=begin,
		subsequent_indent = begin) for f in l]
	if sep == '\n': sep += begin
	return (sep+begin).join(ll)


def RCleanArray(x,options=['nan','inf'],atol=1e-8):
	"""
	Will remove the unsuitable elements from the array.
		- option in ['nan','inf','neg_inf','pos_inf','zero','neg','pos']
		- atol : precision when compare to zero
	Output :
		- new_array  : the array cleaned
		- to_keep    : the array of index to keep from x
			(i in to_keep means that x[i] is kept in the new array)
		- bool_array : the array of bool to keep from x
			(bool_array[i]==True means that x[i] is kept in the new array)
	"""
	bool_array = np.ones(x.shape,dtype=bool)
	if 'nan'       in options :
		bool_array = bool_array & (~ np.isnan(x))
	if 'inf'       in options :
		bool_array = bool_array & (~ np.isinf(x))
	if 'neg_inf'   in options :
		bool_array = bool_array & (~ (np.isinf(x) & (x<0)))
	if 'pos_inf'   in options :
		bool_array = bool_array & (~ (np.isinf(x) & (x>0)))
	if 'zero'      in options :
		bool_array = bool_array & (~ np.isclose(x,0,atol=atol))
	if 'neg'       in options :
		bool_array = bool_array & (~(x<0))
	if 'pos'       in options :
		bool_array = bool_array & (~(x>0))
	to_keep = bool_array.nonzero()[0]
	return x[to_keep],to_keep,bool_array

class RBell:
	def __init__(self,l=1,sound='message-new-instant'):
		"""
		Will ring a bell
		l : int, number of times
		"""

		cmd = ['/usr/bin/canberra-gtk-play']
		if l!=1 : cmd+= ['-l',str(l)]
		cmd += ['--id',sound]
		subprocess.call(cmd)

	@staticmethod
	def availableSounds():
		process = subprocess.Popen(['ls', '/usr/share/sounds/ubuntu/stereo/'], stdout=subprocess.PIPE)
		out, err = process.communicate()
		out = out.decode('utf-8')
		out = out.strip()
		out = out.split('\n')
		out = {o.strip('.ogg') for o in out}
		return out
