

from fpctoolkit.io.file import File

class Potcar(File):
	"""
	Can initialize from an existing potcar file (Potcar('./POTCAR'))
	Can initialize from a string of elements and whether or not to use LDA or GGA (Potcar(['Ba','Ti','O'],lda=False))
		In this case, set of predefined potcars will be used
		Assumes lda = True
	"""

	def __init__(self, file_path=None, elements_list=None):
		super(Potcar,self).__init__(file_path)
		print "1"



