# PYTHON 3
import datetime,re,os
import textwrap
import numpy as np
import subprocess


###################### CONFIG IMPORTATION ##############################
path_to_config = './RFigureConfig/RFigureConfig.py'
file_dir = os.path.realpath(os.path.dirname(__file__))
path_to_config = os.path.join(file_dir,path_to_config)
########################################################################

class RPathFormatting:
    date_replace_dict= { '%Y':'([0-9][0-9][0-9][0-9])',
                    '%y':'([0-9][0-9])',
                    '%m':'([0-9][0-9])',
                    '%d':'([0-9][0-9])',
                    '%H':'([0-2][0-9])',
                    '%I':'([0-1][0-9])',
                    '%p':'({AM,am,Pm,pm})',
                    '%M':'({[0-5][0-9]})',
                    '%S':'({[0-5][0-9]})',
                    '%s':'(.*)',
                    }
    def __init__(self,format,date=None):
        """ Class that will deal with formatting the filepath with the correct
        date.

        Parameters
        ----------
        format : str
            the format to which format the filename. For instance
            "Figure_%Y%m%d_%s" will format the file as `Figure_YYYYMMDD_foo`
            where YYYYMMDD stands for the current date and foo stands for the
            file description.
        date : datetime.datetime instance
            the date at which we have to display the file.
            if None, takes the current date
        """
        self.format = format
        self.date = date

    def interpretFormat(self):
        """ Methods that slits `self.format` in such a way it seperates the date
        relative formatting (%Y, %m, %d, etc.) from the descrition formatting
        (%s). For instance, if the format is `"Figure_%Y%m%d_%s"`; then it will
        return the list `["Figure_%Y%m%d_","%s"]`.

        Returns:
        --------
        formatting : list of str
            the spliting of `self.format` that seperate date formatting from
            decription formatting.
        """
        s = self.format
        formatting = s.split('%s')
        if len(formatting)==1:
            formatting = formatting+['%s']
        else:
            formatting = [x  for y in formatting[:-1] for x in [y,'%s']]+[formatting[-1]]
            formatting = [x for x in formatting if len(x)>0]
        return  formatting

    def checkFormatting(self,filepath):
        """ Checks if the filepath is compatible with the current formatting.

        Parameters
        ----------
        filepath : str
            the filepath to compare with.

        Returns
        -------
        search_result : re.Match or None
            if None, the filpath do not math; otherwise the re.Match instance
            corresponding
        """
        _,filename = os.path.split(filepath)
        filename,_ = os.path.splitext(filename)

        format_re = re.escape(self.format)
        for k,v in self.date_replace_dict.items():
            format_re = format_re.replace(k,v)
        format_re = '^'+format_re
        return re.match(format_re,filename)

    def formatDate(self,date=None):
        """ Return the filename with only the description formatting remain to be
        done.

        Parameters
        ----------
        date : datetime.datetime instance
            the date to consider in the formatting; if none, takes `self.date`;
            (and if `self.date is None`; considers the current day).

        Returns
        -------
        result : str
            the resulting filename with the depent description formatting ready
            to be applyied.

        Example
        -------
        >>> a = RPathFormatting(format="Figure_%Y%m%d_%s")
        >>> a.formatDate(date=datetime.datetime(2020,11,17))
        "Figure_20201117_%s"
        """
        if date is None:
            date=self.date
        if date is None:
            date = datetime.datetime.now()

        res = ''
        for f in self.interpretFormat():
            if  '%s' not in f:
                f = date.strftime(f)
            res += f
        return res

    def getPercentValues(self):
        """ Analyse the format and returns the list of the different percent
        formatting (%Y, %d, %s etc.) in the right order.

        Return
        -------
        res : list of str
            the lisr of the different percent formatting

        Example
        -------
        >>> a = RPathFormatting(format="Figure_%Y%m%d_%s")
        >>> a.getPercentValues()
        ["%Y","%m","%d","%s"]
        """
        positions = {}
        for k in self.date_replace_dict:
            for pos in  [m.start() for m in re.finditer(k,self.format)]:
                positions[pos] = k
        kv = list(positions.items())
        values = [v for _,v in sorted(list(positions.items()))]
        return values

    def formatFilepath(self,filepath,date=None,replace_existing_date=False):
        """ Analyse the format and returns the list of the different percent
        formatting (%Y, %d, %s etc.) in the right order.

        Return
        -------
        res : list of str
            the lisr of the different percent formatting
        replace_existing_date : bool
            if True and `filepath` alreading in a corresponding format
            then, it replaces the date in the failepath

        Example
        -------
        >>> a = RPathFormatting(format="Figure_%Y%m%d_%s")
        >>> a.getPercentValues()
        ["%Y","%m","%d","%s"]
        """
        dirpath,filename = os.path.split(filepath)
        filename,ext = os.path.splitext(filename)
        formatting = self.checkFormatting(filename)
        if formatting:
            values = self.getPercentValues()
            filename = formatting.groups()[values.index('%s')]
            if not replace_existing_date:
                date = self.getDate(filepath)
        filename = self.formatDate(date=date)%filename

        filepath = os.path.join(dirpath,filename+ext)
        return filepath

    def getDate(self,filepath):
        """ Recover the date of the current filepath if it is as the good
        formatting.

        Parameters
        ----------
        filepath : str
            the filepath from which the date has to be retrieved

        Returns
        -------
        date : datetime.datetime instance
            the corresponding datetime

        Example
        -------
        >>> a = RPathFormatting(format="Figure_%Y%m%d_%s")
        >>> a.getDate('foo/Figure_20201117_fii.rfig3')
        datetime.datetime(2020, 11, 17, 0, 0)

        """
        _,filename = os.path.split(filepath)
        filename,_ = os.path.splitext(filename)

        a = self.checkFormatting(filename)
        if not a:
            raise ValueError('The variable `to_get` is not at the correct formatting.')
        values = self.getPercentValues()
        groups = [g for g,v in zip(a.groups(),values) if v!='%s']
        values = [v for v in values if v!='%s']
        date = datetime.datetime.strptime(''.join(groups),''.join(values))
        return date



def RTextWrap(text,nb=79,sep='\n',begin="") :
    """Will return the text properly wrapped

    Parameters
    ----------
    text : str
        the textg to wrap
    nb : int
        the limit at which we wrap the text
    sep : str
        the char that seperate the paragraphs
    begin : str
        the char that should begin each line

    Returns
    -------
    wrapped_text : str
        the wrapped version of the text
    """
    l = text.split(sep)
    ll = [textwrap.fill(f.strip(),nb-len(begin),
        initial_indent=begin,
        subsequent_indent = begin) for f in l]
    if sep == '\n': sep += begin
    return (sep+begin).join(ll)

def decoSetDoc(doc):
    """ Function dedicated to be used as a decorator that set the documentation
     `doc` to the function `func`.

    Parameters
    ----------
    func : fonction
        the function to set the documentation to
    doc : str
        the documentation to attach to the function

    Returns
    -------
    func : fonction
        the function with the given documentation
    """
    def function_deco(func):
        func.__doc__=doc
        return func
    return function_deco

def decoDocFormatting(*args):
    """ Decorator that will format the documentation of the function by using
    the formatting like `doc%args`

    Parameters
    ----------
    args : objects
        the argument to put in the formatting

    Returns
    -------
    func : fonction
        the function with the correct documentation
    """
    def function_deco(func):
        func.__doc__ = func.__doc__%args
        return func
    return function_deco
