import random

from fpctoolkit.util.path import Path
from fpctoolkit.structure_prediction.individual import Individual
from fpctoolkit.workflow.vasp_run_set import VaspRunSet

class Population(object):
	"""
	A collection of individuals. Used for GA structure searching.
	"""

	individual_prefix_string = "individual_"

	def __init__(self, generation_directory_path=None, directory_to_individual_conversion_method=None):
		"""
		If generation_directory_path is not none, loads in existing individuals at this path. If generation_directory_path is None, population is initialized as empty.
		"""
		self.individuals = []
		self.directory_to_individual_conversion_method = directory_to_individual_conversion_method if directory_to_individual_conversion_method else self.default_directory_to_individual_conversion_method

		if generation_directory_path:
			if not Path.exists(generation_directory_path):
				raise Exception("Generation directory path does not exist.")


			self.append_individuals_at_path(generation_directory_path)

	def __str__(self):
		self.sort()
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

	def append_individuals_at_path(self, path):
		"""
		Looks for individuals inside path (saved as directories like 'individual_1, individual_2, ...') and appends to self.individuals
		"""

		#put all valid basenames in list like like: [individual_1, individual_2, ...]
		elligible_directory_basenames = Path.get_list_of_directory_basenames_containing_string(path, Population.individual_prefix_string)

		for basename in elligible_directory_basenames:
			self.individuals.append(self.directory_to_individual_conversion_method(Path.join(path, basename)))


	def default_directory_to_individual_conversion_method(self, path):
		return Individual(calculation_set=VaspRunSet(path=path))


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

		print "get_individual_by_deterministic_tournament_selection called"

		if avoid_individuals_list == None:
			avoid_individuals_list = []

		if len(self.individuals) < (N + len(avoid_individuals_list)):
			raise Exception("Not enough individuals in the population to perform this type of selection")

		self.sort

		print "\n\nafter sorting, pop looks like: "
		print self

		for try_count in range(81):
			if try_count == 80:
				raise Exception("Failed to select individual")
			
			random_number_list = []
			for i in range(N):
				random_number_list.append(random.randint(0, len(self.individuals)-1)) #########fix - selects repeats

			print "random_number_list before sorting: ", random_number_list
			random_number_list.sort()
			print "random_number_list after sorting: ", random_number_list

			individual = self.individuals[random_number_list[0]] #list is sorted - can just take smallest number

			print "Selecting individual ", individual.calculation_set.path
			print "This is index ", random_number_list[0]

			if individual not in avoid_individuals_list:
				return individual
			else:
				print "Avoiding this individual - retrying"
				continue



