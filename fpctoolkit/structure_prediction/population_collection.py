#from fpctoolkit.structure_prediction.population_collection import PopulationCollection



from fpctoolkit.util.path import Path
from fpctoolkit.structure_prediction.population import Population

class PopulationCollection(object):
	"""
	A wrapper class for a directory structure that looks like:

	self.path
		|
		-----generation_1------generation_2------generation_3-------...
				|					|				|
				|					|			   individual_1---...
				|					|
				|				individual_1---...
				|
			individual_1---individual_2----....
				|				|
				|			   ...			
				|
			  relax_1----relax_2----relax_3---...---static

	Convenience methods are included to extract populations out the generation directories.
	"""

	generation_prefix_string = "generation_"

	def __init__(self, path, directory_to_individual_conversion_method=None):
		"""
		directory_to_individual_conversion_method can be left as None - then individuals will load in pickled saved version of instances.
		"""

		self.path = path
		self.directory_to_individual_conversion_method = directory_to_individual_conversion_method
		self.initialize_paths()

	def initialize_paths(self):
		"""
		Creates the base path directory and the first generation's path if they don't already exist.
		"""

		if not Path.exists(self.path):
			Path.make(self.path)

		if self.get_generation_count() == 0:
			Path.make(self.get_next_generation_path())


	def get_generation_count(self):
		"""
		Returns an integer in (0, 1, 2, 3, ...) representing how many generations have been created.
		"""

		i = 1
		while True:
			if not Path.exists(self.get_extended_path(PopulationCollection.generation_prefix_string+str(i))):
				return i - 1

			i += 1


	def get_generation_path_of_generation_number(self, generation_number):
		"""
		Returns the path to generation number generation_number. 
		"""
		return self.get_extended_path(PopulationCollection.generation_prefix_string + str(generation_number))

	def get_current_generation_path(self):
		"""
		Returns the path to the current generation (path may or may not exist) 
		"""
		return self.get_generation_path_of_generation_number(self.get_generation_count())

	def get_last_generation_path(self):
		"""
		Returns the path to the last generation (path may or may not exist) 
		"""
		return self.get_generation_path_of_generation_number(self.get_generation_count()-1)

	def get_next_generation_path(self):
		"""
		Returns the path to the next generation (path may or may not exist) 
		"""
		return self.get_generation_path_of_generation_number(self.get_generation_count()+1)


	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)




	def get_population_of_generation_number(self, generation_number):
		"""
		Returns a population instance populated with individuals from generation number generation_number (doesn't have to be complete). Returns none if generation generation_number doesn't exist yet or is < 1.
		"""

		if (self.get_generation_count() < generation_number) or (generation_number < 1):
			return None
		else:
			return Population(self.get_generation_path_of_generation_number(generation_number), self.directory_to_individual_conversion_method)

	def get_population_of_current_generation(self):
		"""
		Returns a population instance populated with individuals from the current generation (doesn't have to be complete).
		"""

		return self.get_population_of_generation_number(self.get_generation_count())

	def get_population_of_last_generation(self):
		"""
		Returns a population instance populated with individuals from the previous generation. Returns None if the current generation is the first
		"""

		return self.get_population_of_generation_number(self.get_generation_count()-1)

	def get_total_population(self):
		"""
		Returns population instance populated with all individuals (individuals may be complete or incomplete) from all generations (including the current incomplete generation).
		"""

		total_population = Population()

		for i in range(1, self.get_generation_count()+1):
			population = self.get_population_of_generation_number(i)
			total_population.individuals += population.individuals

		return total_population