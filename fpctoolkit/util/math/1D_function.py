#from fpctoolkit.util.math.1D_function import 1DFunction



class 1DFunction(object):

	"""
	Wrapper for mathematical 1-Dimensional numerical functions that look like f(x) -> y. x and y should be real numbers.
	"""


	def __init__(self, 1D_function):
		"""
		1D_function should be some function of one variable (a real number) that returns a real number.
		"""


