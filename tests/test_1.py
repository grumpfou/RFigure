import numpy
import os

from pytest import mark

dir,_ = os.path.split(__file__)
filepath_testfile  = os.path.join(dir,'./Test.rfig3')
filepath_testfile1 = os.path.join(dir,'./Test1.rfig3')

@mark.qt
def test1():
    """
    nothing fancy just make sure it does not crash
    """
    import RFigure,numpy
    X = numpy.arange(0,10,0.1)
    Y = numpy.cos(X)
    i = "plot(X,Y)" # the instrucutions
    d = dict(X=X,Y=Y) # the data to display
    c = "This is a test" # the commentaries associate with the figures
    rf = RFigure.RFigureCore(d=d,i=i,c=c)
    rf.show() # execute the instructions to be sure it works
    rf.save(filepath=filepath_testfile) # only save the rfig3 file
    rf.save(filepath=filepath_testfile,fig_type='pdf')


def test2():
    """
    make sure an existing figure can be openned
    """
    import RFigure,numpy,os
    assert os.path.exists(filepath_testfile)
    rf = RFigure.RFigureCore.load(filepath_testfile)


def test3():
    """
    Test with a pandas DataFrame
    """
    import RFigure,pandas
    a = pandas.DataFrame([[1,1.],[2,-1.],[3,-3]],
                columns=['Exp1','Exp2'],
                index=['First','Second','Thrid'])
    i = "a.plot()\nxticks([0,1,2],a.index)" # the instrucutions
    d = dict(a=a) # the data to display
    c = "This is a test with pandas" # the commentaries associate with the figures
    rf = RFigure.RFigureCore(d=d,i=i,c=c)
    rf.save(filepath=filepath_testfile1) # only save the rfig3 file

def test4():
    """
    make sure an existing figure can be openned
    """
    import RFigure
    assert os.path.exists(filepath_testfile1)
    rf = RFigure.RFigureCore.load(filepath_testfile1)

def test5():
    """
    Ensures that the globals are well respected
    """
    i= '\n'.join([
                "A = np.arange(20)",
                "def aFunc():",
                "	B = np.arange(20)",
                "	return A+B",
                "aFunc()",
                ])

    import RFigure
    # d = dict() # the data to display
    # c = "This is a test with pandas" # the commentaries associate with the figures
    rf = RFigure.RFigureCore(d={},i=i,c='')
    rf.show()
