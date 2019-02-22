from setuptools import setup, find_packages

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
      install_requires=["numpy", "matplotlib", "pyqt5"],
      include_package_data=True,
      scripts=['bin/rfig'],
      # data_files = [("config",['RFigure/RFigureConfig/RFigureHeader.py']),
      #               ("bitmaps",['RFigure/RFigureConfig/RFigureHeader.py',
      #                           ])
      #               ],
      zip_safe=False)
