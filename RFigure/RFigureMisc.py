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
        """ Will return a string containing the date under the format YYYYMMDD.

        Parameters
        - date : int or str
            Which day should be refered. If int, refers to the number of day
            compared to today (negative for the past, positive for the future).
            If str, should be in [""Today", "Yesterday, "Tomorrow"] (by default
            "Today").
        - with_hour : If True return add the hours to the string. The format
            will then be YYYYMMDDHHMMSS.
        """
        dico={
                "Today"     : 0  ,
                "Yesterday" : -1 ,
                "Tomorrow"     : 1  ,
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
