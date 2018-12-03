import RFigure.RFigureGui
import numpy
import os

dir,_ = os.path.split(__file__)
filepath_testfile=os.path.join(dir,'./Test.rfig3')



def test1():
    """
    make sure an existing figure can be openned
    """
    import RFigure.RFigureGui
    assert os.path.exists(filepath_testfile)

    sf = RFigure.RFigureGui.RFigureMainWindow()
    sf.slotOpen(filepath_testfile)


# def test2():
#     """
#     make sure an existing figure can be openned
#     """
#     import RFigure.RFigureGui
#     assert os.path.exists(filepath_testfile)
#
#     sf = RFigure.RFigureGui.RFigureMainWindow()
#     sf.slotOpen(filepath_testfile)
#     sf.rFigureWidget.save(filepath_testfile,force=True)
