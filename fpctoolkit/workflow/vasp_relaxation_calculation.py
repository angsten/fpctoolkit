#from fpctoolkit.workflow.vasp_relaxation_calculation import VaspRelaxationCalculation

import collections
import copy

from fpctoolkit.data_structures.parameter_list import ParameterList
from fpctoolkit.workflow.convenient_vasp_calculation_set_generator import ConvenientVaspCalculationSetGenerator


class VaspRelaxationCalculation(ConvenientVaspCalculationSetGenerator):
	"""
	Collection of runs that form a relaxation.

	Contcar of last run in set always become poscar of next run.

	"""

	external_relax_basename_string = "relax_"
	static_basename_string = "static"

	def __init__(self, path, initial_structure=None, input_dictionary=None):
		"""
		initial_structure can be a Structure instance or a path to a poscar

		Input dicitonary should look something like:
		input_dictioanry = {
			'external_relaxation_count': 4, #number of relaxation calculations before static
			'kpoints_scheme': 'Gamma', #or ['Gamma', 'Monkhorst'] #in latter example, would use gamma for first, monkhorst for rest, in first example, gamma for all
			'kpoints_list': ['2 2 2', '4 4 4', '4 4 4', '6 6 6', '8 8 8'],
			'vasp_code_type': 'standard', #optional, 'standard' (default) or '100'
			'node_count': [1, 2], #optional, set by system size if ever None
			'potcar_type': 'gga_paw_pbe', #not needed - defaults to 'lda_paw',
			'ediff': [0.001, 0.00001, 0.0000001],
			'encut': [200, 400, 600, 800],
			'potim': [0.1, 0.2, 0.4],
			'nsw': [21, 41, 91],
			#'isif' : [5, 2, 3],
			#any other incar parameters with value as a list
		}

		Any parameters normally in the vaspcalculationset input dictionary can be overwritten above.
		"""

		input_dictionary = copy.deepcopy(input_dictionary)

		vasp_calculation_set_input_dictionary = {}
		external_relaxation_count = input_dictionary.pop('external_relaxation_count')

		for key, value in input_dictionary.items():
			if (not isinstance(value, collections.Sequence)) or isinstance(value, basestring):
				input_dictionary[key] = [value]

		parameter_listed_input_dictionary = {}
		for key, value in input_dictionary.items():
			parameter_listed_input_dictionary[key] = ParameterList(value)

		vasp_calculation_set_input_dictionary['path'] = []
		vasp_calculation_set_input_dictionary['structure'] = [initial_structure]
		vasp_calculation_set_input_dictionary['wavecar_path'] = [None]
		vasp_calculation_set_input_dictionary['chargecar_path'] = [None]
		for i in range(0, external_relaxation_count):
			vasp_calculation_set_input_dictionary['path'].append(Path.join(path, VaspRelaxationCalculation.external_relax_basename_string + str(i+1)))
			vasp_calculation_set_input_dictionary['structure'].append('use_last')
			vasp_calculation_set_input_dictionary['wavecar_path'].append('use_last')
			vasp_calculation_set_input_dictionary['chargecar_path'].append(None)

		vasp_calculation_set_input_dictionary['path'].append(Path.join(path, VaspRelaxationCalculation.static_basename_string))


		vasp_calculation_set_input_dictionary['incar_template'] = ['external_relaxation']*external_relaxation_count + ['static']


		for i in range(0, external_relaxation_count):
			vasp_calculation_set_input_dictionary[key] = []
			for key, value in input_dictionary.items():
				vasp_calculation_set_input_dictionary[key].append(value[i])


		#enforce essential static parameters for last run
		if 'nsw' in vasp_calculation_set_input_dictionary:
			vasp_calculation_set_input_dictionary['nsw'][-1] = 0

		if 'ibrion' in vasp_calculation_set_input_dictionary:
			vasp_calculation_set_input_dictionary['ibrion'][-1] = -1

		print '\n\n'
		print vasp_calculation_set_input_dictionary


		super(VaspRelaxationCalculation, self).__init__(vasp_calculation_set_input_dictionary=vasp_calculation_set_input_dictionary)
