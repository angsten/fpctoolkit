#from fpctoolkit.structure_prediction.selector import Selector
import copy

import fpctoolkit.util.misc as misc


class Selector(object):
	"""
	Implements static methods to select individuals in various ways from a population.
	"""

	@staticmethod
	def get_individual_by_deterministic_tournament_selection(population, number_of_competitors=3):
		"""
		Pits number_of_competitors individuals from population against each other. The one with the highest fitness in this sub-group is chosen.
		"""

		if len(population.individuals) < number_of_competitors:
			raise Exception("Not enough individuals in the population to perform this type of selection")

		population.sort() #sort by fitness - most fit individual is at population[0], least at population[-1]
			
		random_indices_list = misc.get_list_of_unique_random_integers(length=number_of_competitors, min_integer=0, max_integer=len(population)-1)
		random_indices_list.sort()

		return population[random_indices_list[0]]  #population's individuals list is sorted, so we can just return the individuals at the smallest index


	@staticmethod 
	def get_selection_function_for_selecting_N_unique_individuals_by_x_way_deterministic_tournament_selection(number_of_competitors):
		"""
		Returns a tournament selection function by closure (curried function).
		"""

		def selection_function(population, number_of_individuals_to_return):
			if len(population) < ( (number_of_individuals_to_return-1) + number_of_competitors):
				raise Exception("Not enough individuals in population to conduct this selection method.")

			individuals_list = []

			poulation_copy = copy.deepcopy(population)

			for i in range(number_of_individuals_to_return):
				individual = Selector.get_individual_by_deterministic_tournament_selection(population_copy, number_of_competitors=number_of_competitors)
				population_copy.remove_individual(individual)

			return individuals_list

		return selection_function