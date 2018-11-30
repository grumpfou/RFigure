import RFigure
import numpy
import os

dir,_ = os.path.split(__file__)
filepath_testfile=os.path.join(dir,'./Test.rfig3')



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
