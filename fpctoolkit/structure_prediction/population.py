



class Population(object):
	"""
	A collection of individuals. Used for GA structure searching.
	"""

	individual_prefix="individual_"

	def __init__(self, generation_directory_path=None, directory_to_individual_conversion_method=None):
		self.individuals = []

		#If path exists, look for individuals inside (saved as directories like 'individual_1, individual_2, ...')
		if generation_directory_path:
			if not directory_to_individual_conversion_method:
				raise Exception("Must specify a method for converting directories to individuals")

			i = 0
			while True:
				individual_path = Path.join(generation_directory_path, Population.individual_prefix + str(i))

				if Path.exists(individual_path):
					
