import random

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

	def __str__(self):
		self.sort
		return "\n".join(" ".join(str(x) for x in [individual.energy, individual.calculation_set.path, individual.structure_creation_id_string]) for individual in self.individuals)

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

	def get_next_available_individual_path(self, generation_directory_path):

		if not Path.exists(generation_directory_path):
			raise Exception("Generation path does not exist")

		i = 1
		while True:
			individual_path = Path.join(generation_directory_path, Population.individual_prefix_string + str(i))
			if not Path.exists(individual_path):
				return individual_path

			i += 1

	def sort(self):
		"""Sorts self.individuals list by energy"""

		self.individuals = sorted(self.individuals, key = lambda individual: individual.energy)

	def get_individual_by_deterministic_tournament_selection(self, N=3, avoid_individuals_list=None):
		"""
		Pits N individuals against each other, one with lowest energy is automatically chosen.

		does not return individual if in avoid_individuals_list - retries in this case
		"""

		if avoid_individuals_list == None:
			avoid_individuals_list = []

		if len(self.individuals) < (N + len(avoid_individuals_list)):
			raise Exception("Not enough individuals in the population to perform this type of selection")

		self.sort

		for try_count in range(81):
			if try_count == 80:
				raise Exception("Failed to select individual")
			
			random_number_list = []
			for i in range(N):
				random_number_list.append(random.randint(0, len(self.individuals)-1))

			random_number_list.sort()

			individual = self.individuals[random_number_list[0]] #list is sorted - can just take smallest number

			if individual not in avoid_individuals_list:
				return individual
			else:
				continue



