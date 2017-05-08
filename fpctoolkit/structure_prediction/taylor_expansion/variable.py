#from fpctoolkit.structure_prediction.taylor_expansion.variable import Variable




class Variable(object):
	"""
	A variable as part of a taylor expansion. Has a type string and index integer.
	"""

	def __init__(self, type_string, index, centrosymmetry=False):
		"""
		Variable type can be displacement or strain. The index should denote which strain or displacement variable this is by an index.
		"""

		self.value = 0.0
		self.type_string = type_string
		self.index = index
		self.centrosymmetry = centrosymmetry

	def __str__(self):
		if self.type_string == 'strain':
			type_string = 'e'
		elif self.type_string == 'displacement':
			type_string = 'u'

		return type_string + '_' + str(self.index+1)