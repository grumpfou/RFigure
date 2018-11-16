import RFigure
import numpy

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
    rf.save(filepath='./Test.rfig3') # only save the rfig3 file
    rf.save(filepath='./Test.rfig3',fig_type='pdf')
