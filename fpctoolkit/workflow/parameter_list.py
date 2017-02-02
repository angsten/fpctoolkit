



class ParameterList(object):
	"""
	A list with special access features tailored to run parameter lists.

	Useful for using with vasp run sets as the internal parameter
	change list.
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




