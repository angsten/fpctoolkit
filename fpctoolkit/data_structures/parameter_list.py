#from fpctoolkit.data_structures.parameter_list import ParameterList



class ParameterList(object):
	"""
	A list with special access features tailored to unknown length parameter lists.

	Basic feature: Same as lists but if an element beyond len(list) is accessed, the len(list)-1 item is returned.


	a = [2, 3, 5]

	a[1] returns 3
	a[3] returns 5
	a[199] returns 5
	"""

	def __init__(self, parameter_list):
		self._parameter_list = parameter_list

	def __getitem__(self, index):
		if (not isinstance(index, int)) or index < 0:
			raise KeyError()
		else:
			if index < len(self._parameter_list):
				return self._parameter_list[index]
			elif len(self._parameter_list) > 0:
				return self._parameter_list[-1]
			else:
				raise Exception("No elements in parameter list")




