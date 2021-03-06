#from fpctoolkit.workflow.vasp_calculation_set import VaspCalculationSet

import collections
import copy

from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_calculation_generator import VaspCalculationGenerator


class VaspCalculationSet(object):
	"""
	Abstract calculation set class - any collection of vasp calculations.

	These runs operate in paralell/series like so:

	self.vasp_calculations_list = [vasp_calc_1, vasp_calc_2, [vcalc_3, vcalc_3_2], vcalc_4] ...]

	The inputs take the same form:

	list_of_vasp_calculation_input_dictionaries = [inputs_dict_1, [inputs_dict_2, inputs...], ...] - see vasp_calculation_generator for how these inputs should look

	vcalc_2 waits for 1 to finish, but vcalc 3 and 3_2 both go at the same time.
	vcalc_4 waits for both previous two to finish.

	Calculations sets are just lists of calculations, and can thus be added together

	v_set_total = vrelax_set
	v_set_total += v_nmr_set #keeps same path as v_set_total, adds on new runs
	"""

	def __init__(self, list_of_vasp_calculation_input_dictionaries=None):
		# self.path = Path.clean(path)

		self.list_of_vasp_calculation_input_dictionaries = copy.deepcopy(list_of_vasp_calculation_input_dictionaries)

		#Turn lone elements into a parallel group of calculations (with only one calculation)
		for i in range(len(self.list_of_vasp_calculation_input_dictionaries)):
			if not isinstance(self.list_of_vasp_calculation_input_dictionaries[i], collections.Sequence):
				self.list_of_vasp_calculation_input_dictionaries[i] = [self.list_of_vasp_calculation_input_dictionaries[i]]
		
		# for vasp_calculation_input_dictionary_parallel_group in self.list_of_vasp_calculation_input_dictionaries:
		# 	for vasp_calculation_input_dictionary in vasp_calculation_input_dictionary_parallel_group:
		# 		vasp_calculation_input_dictionary['path'] = Path.join(self.path, vasp_calculation_input_dictionary['path'])

	def update(self):

		complete = True
		for vasp_calculation_input_dictionary_parallel_group in self.list_of_vasp_calculation_input_dictionaries:
			for vasp_calculation_input_dictionary in vasp_calculation_input_dictionary_parallel_group:

				vasp_calculation = VaspCalculationGenerator(vasp_calculation_input_dictionary)

				if not vasp_calculation.update():
					complete = False

			if not complete:
				return False

		return True

	@property
	def calculations_list(self):
		calculations_list = []
		for vasp_calculation_input_dictionary_parallel_group in self.list_of_vasp_calculation_input_dictionaries:
			sub_list = []
			for vasp_calculation_input_dictionary in vasp_calculation_input_dictionary_parallel_group:

				calculation_path = vasp_calculation_input_dictionary['path']

				if not Path.exists(calculation_path):
					vasp_calculation = None
				else:
					vasp_calculation = VaspCalculationGenerator(vasp_calculation_input_dictionary)
					
				sub_list.append(vasp_calculation)

			calculations_list.append(sub_list)

		return calculations_list

	@property
	def complete(self):
		for vasp_calculation_parallel_group in self.calculations_list:
			for vasp_calculation in vasp_calculation_parallel_group:

				if (vasp_calculation == None) or (not vasp_calculation.complete):
					return False

		return True

	def get_energies_list(self, per_atom=False):
		energies_list = []
		for vasp_calculation_parallel_group in self.calculations_list:
			sub_list = []
			for vasp_calculation in vasp_calculation_parallel_group:

				if not vasp_calculation == None:
					sub_list.append(vasp_calculation.get_final_energy(per_atom=per_atom))
				else:
					sub_list.append(None)

			energies_list.append(sub_list)
				
		return energies_list

	def get_final_structures_list(self, per_atom=False):
		final_structures_list = []
		for vasp_calculation_parallel_group in self.calculations_list:
			sub_list = []
			for vasp_calculation in vasp_calculation_parallel_group:

				if not vasp_calculation == None:
					sub_list.append(vasp_calculation.get_final_structure())
				else:
					sub_list.append(None)
				

			final_structures_list.append(sub_list)
				
		return final_structures_list

	def get_final_energy(self, per_atom):

		if not self.complete:
			return None
		else:
			calculations_list = self.calculations_list

			if len(calculations_list[-1]) > 1:
				raise Exception("Final energy is ambibuous - multiple ending runs.")
			else:
				return calculations_list[-1][0].get_final_energy(per_atom=per_atom)

	def get_final_structure(self):

		if not self.complete:
			return None
		else:
			calculations_list = self.calculations_list

			if len(calculations_list[-1]) > 1:
				raise Exception("Final structure is ambibuous - multiple ending runs.")
			else:
				return calculations_list[-1][0].get_final_structure()

	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)

	# def __iadd__(self, new_vasp_calcualtions_list):
	# 	self.vasp_calculations_list = self.vasp_calculations_list + new_vasp_calcualtions_list
	# 	return self

