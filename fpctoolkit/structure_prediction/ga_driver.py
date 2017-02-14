

from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.structure_prediction.individual import Individual

class GADriver(object):
	"""
	Abstract parent class defining the specifics of the GA search, including operators and how 
	individual calculation sets are defined
	"""

	def __init__(self, ga_input_dictionary, calculation_set_input_dictionary):
		"""
		At minimum, ga_input_dictionary looks like:

		{
			random_fraction = [1.0, 0.3, 0.2, ...]
			mate_fraction = [0.0, 0.7, 0.8, ...]
		}

		Can also contain species lists, constraints, etc.
		"""

		self.input_dictionary = input_dictionary
		self.calculation_set_input_dictionary = calculation_set_input_dictionary

	def get_individual(self, generation_number):
		"""
		Main workhorse - supplies an individual by randomly chosen means (heredity, random, mutate, ...etc.)
		"""

		return ...

	def get_structure(self, generation_number):
		pass

	def get_random_structure(self):
		return None

	def get_mated_structure(self):
		return None

	def get_mutated_structure(self):
		return None

	def get_permuted_structure(self):
		return None


	def directory_to_individual_conversion_method(self, path):
		"""Default to a vasp relaxation"""

		return Individual(calculation_set=VaspRelaxation(path, self.calculation_set_input_dictionary))