#from fpctoolkit.workflow.convenient_vasp_calculation_set_generator import ConvenientVaspCalculationSetGenerator

import collections
import copy

from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_calculation_set_generator import VaspCalculationSetGenerator


class ConvenientVaspCalculationSetGenerator(VaspCalculationSetGenerator):
	"""
	The inputs to this class are explicit with all data for each calculation in the workflow specified in a list like so:

    vasp_calculation_set_input_dictionary = {
	    'path': ['./relaxation/relax_1', ['./relaxation/relax_2', './relaxation/relax_2_2']], #where the vasp_calculation goes - every part must be filled in
	    'structure': ['./POSCAR', ['use_last', 'use_last']], #each must be a Structure instance, a path, or 'use_last'. The latter uses the last calculation's contcar
	    'wavecar_path': [None, ['use_last', 'use_last']], #if not present or None, no wavecar is used. 'use_last' uses last wavecar.
	    'chargecar_path': [None, [None, None]], #if not present, no chargecar is used. Can put 'use_last' as well
	    'kpoints_scheme': ['Gamma', ['Monkhorst', 'Gamma']],      #not essential if kspacing in incar is set
	    'kpoints_list': ['4 4 4', ['4 4 4', '6 6 6']],
	    'potcar_type': 'lda_paw',       #'lda_paw'  or 'gga_paw_pbe', ###if only one non-sequence value is given, this value is used for all calculations for this key
	    'vasp_code_type': 'standard',   #'standard' or '100' for out-of-plane only relaxation
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

		paths_data_list = vasp_calculation_set_input_dictionary['path']


		for key in keys:
			if key in ['path', 'structure']: #these must have all values in the list explicitly included
				continue

			value = vasp_calculation_set_input_dictionary[key]
			
			if (not isinstance(value, collections.Sequence)) or (isinstance(value, basestring)): #only one value given - use this for all

				new_data_list = []

				for i, path_group in enumerate(paths_data_list):

					if (not isinstance(path_group, collections.Sequence)) or isinstance(path_group, basestring):
						path_group = [path_group]

					new_data_group = []
					for j, path in enumerate(path_group):
						new_data_group.append(value)

					new_data_list.append(new_data_group)

				vasp_calculation_set_input_dictionary[key] = new_data_list



		for key in ['structure', 'wavecar_path', 'chargecar_path']:
			print 'key is ' + key
			data = vasp_calculation_set_input_dictionary[key]

			for i in range(1, len(data)):
				value_set = data[i]

				print 'data is ' + str(value_set)

				if (not isinstance(value_set, collections.Sequence)) or (isinstance(value_set, basestring)):
					vasp_calculation_set_input_dictionary[key][i] = [value_set]

				for j, value in enumerate(vasp_calculation_set_input_dictionary[key][i]):
					
					print 'value is ' + value

					if value == 'use_last':
						last_path = vasp_calculation_set_input_dictionary['path'][i-1]

						if isinstance(last_path, collections.Sequence) and (not isinstance(last_path, basestring)):
							raise Exception("Cannot use 'use_last' for path - last_path is ambiguous: " + str(last_path))
						else:
							if key == 'structure':
								append = 'CONTCAR'
							elif key == 'wavecar_path':
								append = 'WAVECAR'
							elif key == 'chargecar_path':
								append = 'CHGCAR'

							vasp_calculation_set_input_dictionary[key][i][j] = Path.join(vasp_calculation_set_input_dictionary['path'][i-1], append)

		print '\n\n'
		print vasp_calculation_set_input_dictionary

		super(ConvenientVaspCalculationSetGenerator, self).__init__(vasp_calculation_set_input_dictionary=vasp_calculation_set_input_dictionary)
