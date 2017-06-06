# RFigure version 3

## Forewords

RFigure is a program that deals save in a specific file (whose extension is
rfig3) the data and the code that is needed to produce a matplotlib figure.
When creating a rfig3 file, is saved separately the data to display and the
instricutions executed to display.

This code is written by R. Dessalles (Grumpfou) for the most part (the only
excpetions are the code in REditors that are adapted from example on the web).
It is proposed under the license GNU General Public License v3.0. It is written
in Python 3.5.2.

## External libraries needed

- matplotlib (tested with version 2.0.1)
- numpy (tested with version 1.12.1)
- PyQt5

## Quick Example
```
> import RFigure3,numpy
> X = numpy.arange(0,10,0.1)
> Y = numpy.cos(X)
> i = "plot(X,Y)" # the instrucutions
> d = dict(X=X,Y=Y) # the data to display
> c = "This is a test" # the commentaries associate with the figures
> rf = RFigure3.RfigureCore(d=d,i=i,c=c,figname='Test',dirpath='.')
> rf.show() # execute the instrucutions to be sure it works
> rf.save() # only save the rfig3 file
> rf.save(fig_type='pdf') # save the rfig3 file as well as the pdf aoscciated
```
Once a rfig3 file is saved, one can use the gui interface to modify the
instructions:
> $ python3 /foo/RFigure3.py ./Test.rfig3

![](./ExampleGui.png)

## How the code is oraganized

- RFigure3: contains the main two classes (RFigureCore and RFigureGui) used to
handle rfig3 files. RFigureCore is a direct tool used in the scripts to create
the files. RFigureGui is a gui interface used to modify aposteriori the
instructions
- RFigureConfig: contains the header that will be execute before any
instructions. It typically import numpy and matplotlib as the magic function
%pyplot does in Jupyter/IPython
- RPickle2: handels the coding and decoding of information contained in rfig3
files. Works in the same way as the regular pickle library of python
- REditors: contains the Syntax Highlighters used to display the python code
(for the instructions) and the markdown code (for the commentaries).

## Miscelanous
- Local Header: When the program detect a file with the name
.RFigureHeaderLocal.py in the same dir as the file, it adds it to the header
(can be used to specify the font for all the rfig3 of the directory for instance).
- Format name: when set to true when save (or push the button in the gui
  interface), it will format the name of the figure as Figure_YYYYMMDD_foo.rfig3
  (where YYYYMMDD stands for the current date).
- Shortcurts: in the Gui interface: Ctrl+S will save the file; Ctrl+M or
Ctrl+Enter will show the figure.
- SF_INSTRUCTIONS command: when the instructions in input contained at some
point the line
> \#! SF_INSTRUCTIONS

the program consider the instruction begins only at this point. It is usefull
when unsing it with a Jupyter notebook:
```
**In[]:**
> X = numpy.arange(0,10,0.1)
> d=dict(X=X)
> rf = RFigure3.RFIgureCore(i=In[-1],d=d)
> rf.save()
> #! SF_INSTRUCTIONS
> X=arange(0,10,0.1)
> plot(X,cos(X))
```
Will save figure whose instructions are the last lines of the cell.

## FAQ

- Why is it RFigure3 (and not 2 or 1) and RPickle2 (and not 1)?
  I had several persional versions of these libraries.
- Why there is a 'R' in front of the modules?
  Because my first name is **R**enaud
- Why do not use the default pickle library of Python ?
  Because there is so much problem of compatibilites between the different
  versions of Python on this module. I better control the data with my own
  Pickle (the inconvienent is that it only deal with basic types)
