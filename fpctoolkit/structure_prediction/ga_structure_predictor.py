

from fpctoolkit.util.path import Path
from fpctoolkit.structure_prediction.population import Population

class GAStructurePredictor(object):
	"""
	Runs a genetic algorithm-based structure search.

	The provided GADriver instance controls the specifics of how this search is implemented.
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

		current_generation_count = self.get_generation_count()

		
		population_of_last_generation = Population(self.get_last_generation_path(), self.ga_driver.directory_to_individual_conversion_method) if current_generation_count > 1 else None
		current_population = Population(generation_directory_path=current_generation_path, directory_to_individual_conversion_method=self.ga_driver.directory_to_individual_conversion_method)

		while len(current_population) < self.ga_driver.get_individuals_per_generation(current_generation_count):
			new_individual = self.ga_driver.get_new_individual(current_population.get_next_available_individual_path(current_generation_path), population_of_last_generation, current_generation_count)

			current_population.append(new_individual)


		all_complete = True

		for individual in current_population:
			if not individual.complete:
				individual.update()
				all_complete = False

		print "\n\nPopulation for last generation looks like: \n\n" + str(population_of_last_generation)
		print "\n\nPopulation for this generation looks like: \n\n" + str(current_population)

		if all_complete and (current_generation_count < self.ga_driver.get_max_number_of_generations()):
			print "Generation complete. Making next generation path"
			Path.make(self.get_next_generation_path())




	def get_current_generation_path(self):
		generation_count = self.get_generation_count()

		return self.get_extended_path(GAStructurePredictor.generation_prefix_string + str(generation_count)) if generation_count > 0 else None

	def get_last_generation_path(self):
		generation_count = self.get_generation_count()

		return self.get_extended_path(GAStructurePredictor.generation_prefix_string + str(generation_count-1)) if generation_count > 1 else None

	def get_next_generation_path(self):
		generation_count = self.get_generation_count()

		return self.get_extended_path(GAStructurePredictor.generation_prefix_string + str(generation_count+1))

	def get_generation_count(self):
		i = 1
		while True:
			if not Path.exists(self.get_extended_path(GAStructurePredictor.generation_prefix_string + str(i))):
				return i - 1

			i += 1


	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)

	def get_total_population(self):
		"""
		Returns population instance with all individuals from all generations in it
		"""

		total_population = Population()

		for i in range(self.get_generation_count()):
			population = Population(self.get_extended_path(GAStructurePredictor.generation_prefix_string + str(i+1)), self.ga_driver.directory_to_individual_conversion_method)
			total_population.individuals += population.individuals


		return total_population