



class GAStructurePredictor(object):
	"""
	Runs a genetic algorithm-based structure search.

	GADriver instance specifies the specifics of how this search is implemented.
	"""

	generation_prefix_string = ""

	def __init__(self, path, ga_driver):
		self.path = path
		self.ga_driver = ga_driver


	def update(self):

		Path.make(self.path)




	def get_current_generation_path(self):


	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)