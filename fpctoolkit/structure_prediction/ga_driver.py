#from fpctoolkit.structure_prediction.ga_driver import GADriver

import random
import copy

from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.structure_prediction.individual import Individual
from fpctoolkit.workflow.parameter_list import ParameterList
from fpctoolkit.util.random_selector import RandomSelector

class GADriver(object):
	"""
	Abstract parent class defining the specifics of the GA search, including operators and how individual calculation sets are defined.
	"""

	def __init__(self, ga_input_dictionary, calculation_set_input_dictionary, selection_function, random_structure_creation_function, structure_mating_function):
		"""
		ga_input_dictionary controls how operators are performed and the rates at which various operators are randomly chosen to generate a new individual (a structure).

		At minimum, ga_input_dictionary looks like:

		{
			'max_number_of_generations': 15,
			'individuals_per_generation': [50, 40, 30], (flexible parameter list)
			'random_fractions_list': [1.0, 0.3, 0.2, ...],
			'mate_fractions_list': [0.0, 0.7, 0.8, ...]
		}

		ga_input_dictionary can also contain species lists, constraints, etc => dependent on the child class implementation.

		selection_function is any function that looks like selection_function(population, number_of_individuals_to_return) and returns 
		a list of individuals of length number_of_individuals_to_return that were selected from population.

		See VaspRelaxation class for an example of what calculation_set_input_dictionary should look like. This input_dictionary
		determines how the actual calculations are carried out for each individual in the population.
		"""

		self.ga_input_dictionary = ga_input_dictionary
		self.selection_function = selection_function
		self.calculation_set_input_dictionary = calculation_set_input_dictionary

		self.individuals_per_generation = ParameterList(self.ga_input_dictionary['individuals_per_generation'])

		self.random_fractions_list = ParameterList(self.ga_input_dictionary['random_fractions_list']) if 'random_fractions_list' in self.ga_input_dictionary else ParameterList([0.0])
		self.mate_fractions_list = ParameterList(self.ga_input_dictionary['mate_fractions_list']) if 'mate_fractions_list' in self.ga_input_dictionary else ParameterList([0.0])
		self.mutate_fractions_list = ParameterList(self.ga_input_dictionary['mutate_fractions_list']) if 'mutate_fractions_list' in self.ga_input_dictionary else ParameterList([0.0])
		self.permute_fractions_list = ParameterList(self.ga_input_dictionary['permute_fractions_list']) if 'permute_fractions_list' in self.ga_input_dictionary else ParameterList([0.0])

		self.structure_creation_id_string = None #will track how the individual's structure was created
		self.parent_structures_list = None
		self.parent_paths_list = None


	def directory_to_individual_conversion_method(self, path):
		"""
		This method controls how to convert a directory containing vasp runs into an individual. The default, as implemented by this parent class, will be to return an
		individual whose calculation set is a vasp relaxation instance.
		"""

		return Individual(calculation_set=VaspRelaxation(path=path, input_dictionary=copy.deepcopy(self.calculation_set_input_dictionary)))


	def create_new_individual(self, individual_path, population_of_last_generation, generation_number):
		"""
		This method will create (and return) a new individual whose initial structure was created by randomly chosen means (heredity, random, mutate, ...etc.)
		"""

		initial_structure = self.get_structure(population_of_last_generation, generation_number)

		relaxation = VaspRelaxation(path=individual_path, initial_structure=initial_structure, input_dictionary=copy.deepcopy(self.calculation_set_input_dictionary))

		return Individual(calculation_set=relaxation, structure_creation_id_string=self.structure_creation_id_string, parent_structures_list=self.parent_structures_list, parent_paths_list=self.parent_paths_list)


	def get_max_individuals_count_of_generation_number(self, generation_number):
		"""
		Returns the number of individuals to be created in generation generation_number.
		"""

		return self.individuals_per_generation[generation_number-1]

	def get_max_number_of_generations(self):
		return self.ga_input_dictionary['max_number_of_generations']


	def get_structure(self, population_of_last_generation, generation_number):
		"""
		Returns a structure generated by one of the randomly selected operators (such as heredity, mutation, ...). The probability of a given operator being used to generate
		a structure is dependent on the input probability lists for each operator and the current generation number.
		"""
		
		probabilities_list = []
		probabilities_list.append(self.random_fractions_list[generation_number-1])
		probabilities_list.append(self.mate_fractions_list[generation_number-1])
		probabilities_list.append(self.mutate_fractions_list[generation_number-1])
		probabilities_list.append(self.permute_fractions_list[generation_number-1])

		random_selector = RandomSelector(probabilities_list)
		event_index = random_selector.get_event_index()

		if event_index == 0:
			return self.get_random_structure(population_of_last_generation)
		elif event_index == 1:
			return self.get_mated_structure(population_of_last_generation)
		elif event_index == 2:
			return self.get_mutated_structure(population_of_last_generation)
		elif event_index == 3:
			return self.get_permuted_structure(population_of_last_generation)


	def get_random_structure(self, population_of_last_generation):
		self.structure_creation_id_string = 'random'
		self.parent_structures_list = None
		self.parent_paths_list = None

		return self.random_structure_creation_function()

	def get_mated_structure(self, population_of_last_generation):
		self.structure_creation_id_string = 'mating'

		individuals_list = self.selection_function(population=population_of_last_generation, number_of_individuals_to_return=2)

		self.parent_structures_list = [copy.deepcopy(individual.final_structure) for individual in individuals_list]
		self.parent_paths_list = [individual.calculation_set.path for individual in individuals_list]

		return self.structure_mating_function(self.parent_structures_list[0], self.parent_structures_list[1])

	def get_mutated_structure(self, population_of_last_generation):
		return None

	def get_permuted_structure(self, population_of_last_generation):
		return None

