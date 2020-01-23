from setuptools import setup, find_packages
import platform

if platform.system()[0]=='Windows':
    install_requires = ["numpy", "matplotlib", "pyqt5"]
    isWin = True
else:
    install_requires = ["numpy", "matplotlib"]
    isWin = False



setup(name='rfigure',
      version='3.0',
      description='Creation and edition of figures with Python',
      long_description="""RFigure is a program that deals save in a specific file (whose extension is
      rfig3) the data and the code that is needed to produce a matplotlib figure.""",
      classifiers=[
        'Development Status :: 3.0',
        'License :: GPL-3.0',
        'Programming Language :: Python :: 3.7',
        'Topic :: Image processing :: Matplotlib',
      ],
      keywords='figure image plot matplotlib',
      python_requires='>=3.6',
      url='https://github.com/grumpfou/RFigure',
      author='Renaud Dessalles',
      author_email='see on my website',
      license='GPL-3.0',
      packages=find_packages(),
      package_data = {'RFigure':['images/*.png']},
      install_requires=install_requires,
      include_package_data=True,
      # entry_points={
      #           'gui_scripts': ['rfigt = bin/rfig'],
      #               },
      scripts=['bin/rfig'],
      data_files = [("config",['RFigure/RFigureConfig/RFigureHeader.py']),
                    # ("bitmaps",['RFigure/RFigureConfig/RFigureHeader.py',
                    #             ])
                    ],
      entry_points = {
          'console_scripts': [
              'rfig = RFigure.RFigureGui:main',
              ]
      },
zip_safe=False)
if not isWin:
    print('IMPORTANT: Since you are not in Windows, you will need to install PyQt5 by hand. Try something like \n'
          'mylogin:$ sudo apt-get install python-qt5')
