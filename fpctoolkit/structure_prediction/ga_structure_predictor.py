

from fpctoolkit.util.path import Path
from fpctoolkit.structure_prediction.population import Population

class GAStructurePredictor(object):
	"""
	Runs a genetic algorithm-based structure search.

	The directory structure looks like:

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

	The provided GADriver instance controls the specifics of how this search is implemented.
	"""

	generation_prefix_string = "generation_"

	def __init__(self, path, ga_driver):
		self.path = path
		self.ga_driver = ga_driver

		self.initialize_paths()

	def initialize_paths(self):
		"""
		Creates the base path directory and the first generation's path if they don't already exist.
		"""

		if not Path.exists(self.path):
			Path.make(self.path)

		if self.get_generation_count() == 0:
			Path.make(self.get_next_generation_path())

	def update(self):
		"""
		Main update loop - create individuals until quota is reached and also update the individuals that have been created in this generation.
		"""
			
		current_generation_path = self.get_current_generation_path()
		current_generation_count = self.get_generation_count()
		
		population_of_last_generation = self.get_population_of_last_generation()
		current_population = self.get_population_of_current_generation()




		all_complete = True
		for individual in current_population:
			if not individual.complete:
				individual.update()
				all_complete = False


		if all_complete and (current_generation_count < self.ga_driver.get_max_number_of_generations()):
			print "Generation complete. Making next generation path"
			Path.make(self.get_next_generation_path())

	def populate_generation(self):
		"""
		Create additional individuals until the current generation has been fully populated.
		"""

		population_of_last_generation = self.get_population_of_last_generation()
		current_population = self.get_population_of_current_generation()

		while len(current_population) < self.ga_driver.get_max_individuals_count_of_generation_number(self.get_generation_count()):
			new_individual = self.ga_driver.get_new_individual(current_population.get_next_available_individual_path(self.get_current_generation_path()), population_of_last_generation, self.get_generation_count())
			current_population.append(new_individual)


	def get_generation_count(self):
		"""
		Returns an integer in (0, 1, 2, 3, ...) representing how many generations have been created.
		"""

		i = 1
		while True:
			if not Path.exists(self.get_extended_path(GAStructurePredictor.generation_prefix_string+str(i))):
				return i - 1

			i += 1


	def get_population_of_generation_number(self, generation_number):
		"""
		Returns a population instance populated with individuals from generation number generation_number (doesn't have to be complete). Returns none if generation generation_number doesn't exists yet or is < 1.
		"""

		if (self.get_generation_count() < generation_number) or (generation_number < 1):
			return None
		else:
			return Population(self.get_generation_path_of_generation_number(generation_number), self.ga_driver.directory_to_individual_conversion_method)

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



	def get_generation_path_of_generation_number(self, generation_number):
		"""
		Returns the path to generation number generation_number. 
		"""
		return self.get_extended_path(GAStructurePredictor.generation_prefix_string + str(generation_number))

	def get_current_generation_path(self):
		"""
		Returns the path to the current generation (path may or may not exist) 
		"""
		return self.get_generation_path_of_generation_number(self.generation_count())

	def get_last_generation_path(self):
		"""
		Returns the path to the last generation (path may or may not exist) 
		"""
		return self.get_generation_path_of_generation_number(self.generation_count()-1)

	def get_next_generation_path(self):
		"""
		Returns the path to the next generation (path may or may not exist) 
		"""
		return self.get_generation_path_of_generation_number(self.generation_count()+1)


	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)




	def get_total_population(self):
		"""
		Returns population instance populated with all individuals (which may be complete or incomplete) from all generations (including the current incomplete generation).
		"""

		total_population = Population()

		for i in range(self.get_generation_count()):
			population = Population(self.get_extended_path(GAStructurePredictor.generation_prefix_string + str(i+1)), self.ga_driver.directory_to_individual_conversion_method)
			total_population.individuals += population.individuals


		return total_population