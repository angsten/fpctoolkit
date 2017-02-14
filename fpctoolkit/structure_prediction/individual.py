



class Individual(object):
	"""
	Individual for Genetic Algorithm structure searches.
	Just a calculation_set class wrapper with some added functionalities.
	"""

	def __init__(self, calculation_set):
		self.calculation_set = calculation_set


	@property
	def energy(self):
		return self.calculation_set.get_final_energy(per_atom=True) 

	@property
	def initial_structure(self):
		return self.calculation_set.initial_structure

	@property
	def complete(self):
		return self.calculation_set.complete

	@property
	def final_structure(self):
		return self.calculation_set.final_structure