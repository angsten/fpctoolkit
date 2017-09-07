#from fpctoolkit.workflow.vasp_calculation_set_generator import VaspCalculationSetGenerator

import collections
import copy

from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_calculation_set import VaspCalculationSet


class VaspCalculationSetGenerator(VaspCalculationSet):
	"""
	The inputs to this class are explicit with all data for each calculation in the workflow specified in a list like so:

	vasp_calculation_set_input_dictionary = {
	    'path': ['./relaxation/relax_1', ['./relaxation/relax_2', './relaxation/relax_2_2']], #where the vasp_calculation goes
	    'structure': ['./POSCAR', ['./relaxation/relax_1/CONTCAR', './relaxation/relax_1/CONTCAR']], #could also be a path like './poscar', in which case it become the contcar_path for the first run
	    'wavecar_path': [None, ['./relaxation/relax_1/WAVECAR', './relaxation/relax_1/WAVECAR']], #if not present, no wavecar is used
	    'chargecar_path': [None, [None, None]], #if not present, not chargecar is used
	    'kpoints_scheme': ['Gamma', ['Monkhorst', 'Gamma']],      #not essential if kspacing in incar is set
	    'kpoints_list': ['4 4 4', ['4 4 4', '6 6 6']],
	    'potcar_type': ['lda_paw', ['lda_paw', 'lda_paw']],       #'lda_paw'  or 'gga_paw_pbe',
	    'vasp_code_type': ['standard', ['standard', 'standard']],   #'standard' or '100' for out-of-plane only relaxation
	    'node_count': [1, [2, 4]],                 #auto-set based on system size and host if not present
	    'incar_template': ['external_relaxation', ['static', 'static']],      #if key not there, just creates a custom incar, can be 'static' or 'external_relaxation'
	    'encut': [400, [500, 600]],
	    'ediff': [1e-5, [1e-6, 1e-7]],
	    #'kspacing': 0.5,    #if this is specified, don't need kpoints info below
	    #'kgamma': True,
	    #'lreal': False,     #set based on system size if lreal key is not present,
	    #'npar': 4,          #will be 4 regardless of system size or:
	    #'npar': None, #npar will not be in incar no matter what or:
	    #npar key not present (auto-set based on system size and host)
	    #any other incar modifiers
    }

	"""

	def __init__(self, vasp_calculation_set_input_dictionary=None):
		# self.path = Path.clean(path)
		
		vasp_calculation_set_input_dictionary = copy.deepcopy(vasp_calculation_set_input_dictionary)
		vasp_calculation_set_input_dictionary = {k.lower(): v for k, v in vasp_calculation_set_input_dictionary.items()} #enforce all keys lowercase


		keys = vasp_calculation_set_input_dictionary.keys()

		


		for key in keys:
			data_list = vasp_calculation_set_input_dictionary[key]

			for i in range(len(data_list)):
				if (not isinstance(data_list[i], collections.Sequence)) or (isinstance(data_list[i], basestring)):
					data_list[i] = [data_list[i]]


		#now we need to make sure all of the data_lists have the same shape
		paths_data_list = vasp_calculation_set_input_dictionary['path']

		for key in keys:
			data_list = vasp_calculation_set_input_dictionary[key]

			if len(data_list) != len(paths_data_list):
				raise Exception("vasp calculation set input dictionary does not have all same shape: ", paths_data_list, data_list)

			for i, data_item in enumerate(data_list):
				path_data_item = paths_data_list[i]

				if len(data_item) != len(path_data_item):
					raise Exception("vasp calculation set input dictionary does not have all same shape: ", path_data_item, data_item)					



		list_of_vasp_calculation_input_dictionaries = []
		for i, path_group in enumerate(paths_data_list):

			vasp_calculation_input_group = []

			for j, path in enumerate(path_group):
				vasp_calculation_input_dictionary = {}

				for key in keys:
					vasp_calculation_input_dictionary[key] = vasp_calculation_set_input_dictionary[key][i][j]					

				vasp_calculation_input_group.append(vasp_calculation_input_dictionary)

			list_of_vasp_calculation_input_dictionaries.append(vasp_calculation_input_group)

		# print '\n\nvasp_calc_set_gen:'
		# print list_of_vasp_calculation_input_dictionaries

		super(VaspCalculationSetGenerator, self).__init__(list_of_vasp_calculation_input_dictionaries=list_of_vasp_calculation_input_dictionaries)
