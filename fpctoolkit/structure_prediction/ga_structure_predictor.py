

from fpctoolkit.util.path import Path
from fpctoolkit.strucutre_prediction.population import Population

class GAStructurePredictor(object):
	"""
	Runs a genetic algorithm-based structure search.

	GADriver instance specifies the specifics of how this search is implemented.
	"""

	generation_prefix_string = "generation_"

	def __init__(self, path, ga_driver):
		self.path = path
		self.ga_driver = ga_driver


	def update(self):

		Path.make(self.path)

		current_generation_path = self.get_current_generation_path()

		if not current_generation_path:
			Path.make(self.get_next_generation_path())
			current_generation_path = self.get_current_generation_path()

		population = Population(current_generation_path)

		current_generation_count = self.get_generation_count()

		while len(population) < self.ga_driver.get_individuals_per_generation_count(current_generation_count):
			new_individual = self.ga_driver.get_new_individual(population.get_next_available_individual_path(current_generation_path), population_of_last_generation, current_generation_count)

			population.append(new_individual)


		all_complete = True

		for each individual in population:

			if not individual.complete:
				individual.update()
				all_complete = False

		if all_complete and (current_generation_count < self.ga_driver.get_max_number_of_generations()):
			Path.make(self.get_next_generation_path())



	def get_current_generation_path(self):
		generation_count = self.get_generation_count()

		if generation_count == 0:
			return None
		else:
			return self.get_extended_path(GAStructurePredictor.generation_prefix_string + str(generation_count))

	def get_next_generation_path(self):
		generation_count = self.get_generation_count()

		return self.get_extended_path(GAStructurePredictor.generation_prefix_string + str(generation_count+1))

	def get_generation_count(self):
		i = 1
		while True:
			if not Path.exists(self.get_extended_path(GAStructurePredictor.generation_prefix_string + str(i))):
				return i - 1

			i += 1

		#return len(Path.get_list_of_directory_basenames_containing_string(GAStructurePredictor.generation_prefix_string))


	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)