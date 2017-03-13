


from fpctoolkit.util.path import Path
from fpctoolkit.structure_prediction.population_collection import PopulationCollection

class GAStructurePredictor(object):
	"""
	Runs a genetic algorithm-based structure search.

	The actual populations and their directory-structure realizations are stored in a PopulationCollection instance. See this class for how the directories are structured.

	The provided GADriver instance controls the specifics of how this search is implemented.
	"""

	def __init__(self, path, ga_driver):
		self.ga_driver = ga_driver
		self.population_collection = PopulationCollection(path, self.ga_driver.directory_to_individual_conversion_method)

	def update(self):
		"""
		Main update method - create individuals until quota is reached, update the individuals in the current generation, create next generation path if current generation is complete.
		"""

		self.populate_current_generation()

		generation_complete = self.update_all_individuals_of_current_generation()

		if generation_complete and (self.population_collection.get_generation_count() < self.ga_driver.get_max_number_of_generations()):
			Path.make(self.population_collection.get_next_generation_path())

	def populate_current_generation(self):
		"""
		Creates additional individuals (and runs one update on them to put them on the queue) until the current generation has been fully populated.
		"""

		current_population = self.population_collection.get_population_of_current_generation()

		while len(current_population) < self.ga_driver.get_max_individuals_count_of_generation_number(self.population_collection.get_generation_count()):

			new_individual = self.ga_driver.create_new_individual(current_population.get_next_available_individual_path(self.population_collection.get_current_generation_path()), 
				self.population_collection.get_population_of_last_generation(), self.population_collection.get_generation_count())

			current_population.append(new_individual)

			new_individual.update()


	def update_all_individuals_of_current_generation(self):
		"""
		Runs update on all individuals in the current generation. Returns True if all individuals are completed.
		"""

		all_complete = True

		for individual in self.population_collection.get_population_of_generation_number(2):#self.population_collection.get_population_of_current_generation():
			if not individual.complete:
				individual.update()
				all_complete = False

		return all_complete


	