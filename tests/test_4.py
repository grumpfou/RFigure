import numpy
import os

from pytest import mark

dir,_ = os.path.split(__file__)
filepath_testfile=os.path.join(dir,'./Test.rfig3')


"""
We test the function find_list_variables
"""
def test1():
    """
    Select variables that are in locals_ and can be RFigurePickled
    """
    from RFigure.RFigureMagics import find_list_variables
    instructions = """
    afunction(a)
    afunction(b)
    afunction(c)
    """
    locals_ = dict(a=1,b=lambda x:x) # b can not be pickled
    res = set(find_list_variables(instructions,locals_))
    assert res=={"a"}

def test2():
    """
    Make sure we do not import the varibales of the for loops, unless they are
    used in the instructions before
    """
    from RFigure.RFigureMagics import find_list_variables
    instructions = """
    afunction(to_keep)

    for to_keep in range(10):
        pass

    for to_remove1, to_remove2 in zip(aa,bb):
        afunction(to_remove1, to_remove2)
        for to_remove3 in aList:
            afunction(to_remove3)

    for to_remove4,(to_remove5,to_remove6) in enumerate(aa):
        afunction(to_remove5)
    """
    locals_ = {"to_remove%i"%i:0 for i in range(1,10)}
    locals_["to_keep"] = 0

    res = set(find_list_variables(instructions,locals_))
    assert res=={"to_keep"}


def test3():
    """
    make sure the parameters name of functions are not considered
    """
    from RFigure.RFigureMagics import find_list_variables
    instructions = """
    afunction(a=3)
    """
    locals_ = dict(a=0)
    res = set(find_list_variables(instructions,locals_))
    assert len(res)==0

    

def test4():
    """
    make sure that there is no problem for the `for ... in ... for ... in` on the smae line
    """
    from RFigure.RFigureMagics import find_list_variables
    instructions = """
    [for to_remove1 in aa]+[for to_remove2 in bb]
    """
    locals_ = dict(a=0)
    res = set(find_list_variables(instructions,locals_))
    assert len(res)==0
