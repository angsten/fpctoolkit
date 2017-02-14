

from fpctoolkit.util.path import Path

class Population(object):
	"""
	A collection of individuals. Used for GA structure searching.
	"""

	individual_prefix_string = "individual_"

	def __init__(self, generation_directory_path=None, directory_to_individual_conversion_method=None):
		self.individuals = []

		#If path exists, look for individuals inside (saved as directories like 'individual_1, individual_2, ...')
		if generation_directory_path:
			if not directory_to_individual_conversion_method:
				raise Exception("Must specify a method for converting directories to individuals")
			elif not Path.exists(generation_directory_path):
				raise Exception("Generation directory path does not exist.")


			elligible_directory_basenames = Path.get_list_of_directory_basenames_containing_string(generation_directory_path, Population.individual_prefix_string)

			for basename in elligible_directory_basenames:
				self.individuals.append(directory_to_individual_conversion_method(Path.join(generation_directory_path, basename)))

	def __len__(self):
		return len(self.individuals)

	def __iter__(self):
		return iter(self.individuals)

	def __getitem__(self, key):
		return self.individuals[key]

	def __setitem__(self, key, value):
		self.individuals[key] = value

	def append(self, value):
		self.individuals.append(value)


	def sort(self):
		"""Sorts self.individuals list by energy"""

		self.individuals = sorted(self.individuals, key = lambda individual: individual.energy)


