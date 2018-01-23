#from fpctoolkit.workflow.vasp_calculation_generator import VaspCalculationGenerator

import copy

from fpctoolkit.util.queue_adapter import QueueAdapter
from fpctoolkit.io.file import File
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.potcar import Potcar
from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.io.vasp.incar import Incar
from fpctoolkit.structure.structure import Structure
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.workflow.vasp_calculation import VaspCalculation
from fpctoolkit.util.path import Path

class VaspCalculationGenerator(VaspCalculation):
	"""
	This class is a vasp calculation - just has a different constructor that is more convenient.

	vasp_calculation_input_dictionary = {
		'path': './calculation', #where the vasp_calculation goes
		'structure': Structure('./poscar'), #could also be a path like './poscar', in which case it become the contcar_path for the first run
		'wavecar_path': './wavecar', #if not present, no wavecar is used
		'chargecar_path': './chargecar', #if not present, not chargecar is used
		'kpoints_scheme': 'Gamma',      #not essential if kspacing in incar is set - can be None or left out in this case
		'kpoints_list': '6 6 4',
		'potcar_type': 'lda_paw',       #'lda_paw'  or 'gga_paw_pbe',
		'vasp_code_type': 'standard',   #'standard' or '100' for out-of-plane only relaxation
		'node_count': 2,                 #auto-set based on system size and host if not present

		'incar_template': 'static',      #if key not there, just creates a custom incar, can be 'static' or 'external_relaxation'
		'encut': 600, #Can also be an integer between 0.1 and 10.0 - in this case, enmax in potcar times this number is used to get encut
		'ediff': 1e-6,
		'kspacing': 0.5,    #if this is specified, don't need kpoints info below
		'kgamma': True,
		'lreal': False,     #set based on system size if lreal key is not present or value is None,
		'npar': 4,          #will be 4 regardless of system size or:
		'npar': 'Remove', #npar will not be in incar no matter what or:
		#npar key not present or value is None (auto-set based on system size and host)
		#any other incar modifiers
	}
	"""

	def __init__(self, vasp_calculation_input_dictionary):

		vasp_calculation_input_dictionary = copy.deepcopy(vasp_calculation_input_dictionary)

		vasp_calculation_input_dictionary = {k.lower(): v for k, v in vasp_calculation_input_dictionary.items()} #enforce all keys lowercase

		path = Path.clean(vasp_calculation_input_dictionary.pop('path'))

		information_structure = None #used for number of nodes and potcar
		if isinstance(vasp_calculation_input_dictionary['structure'], Structure):
			initial_structure = vasp_calculation_input_dictionary.pop('structure')
			information_structure = initial_structure
			contcar_path = None
		else:
			initial_structure = None
			contcar_path = vasp_calculation_input_dictionary.pop('structure')
			information_structure = Structure(contcar_path)

		wavecar_path = vasp_calculation_input_dictionary.pop('wavecar_path') if 'wavecar_path' in vasp_calculation_input_dictionary else None
		chargecar_path = vasp_calculation_input_dictionary.pop('chargecar_path') if 'chargecar_path' in vasp_calculation_input_dictionary else None
		incar_template = vasp_calculation_input_dictionary.pop('incar_template') if 'incar_template' in vasp_calculation_input_dictionary else None
		kpoints_scheme = vasp_calculation_input_dictionary.pop('kpoints_scheme') if 'kpoints_scheme' in vasp_calculation_input_dictionary else None
		kpoints_list = [int(x) for x in vasp_calculation_input_dictionary.pop('kpoints_list').split(' ')] if ('kpoints_list' in vasp_calculation_input_dictionary and vasp_calculation_input_dictionary['kpoints_list'] != None) else None
		potcar_type = vasp_calculation_input_dictionary.pop('potcar_type') if 'potcar_type' in vasp_calculation_input_dictionary else 'lda_paw'
		vasp_code_type = vasp_calculation_input_dictionary.pop('vasp_code_type') if 'vasp_code_type' in vasp_calculation_input_dictionary else 'standard'
		node_count = vasp_calculation_input_dictionary.pop('node_count') if 'node_count' in vasp_calculation_input_dictionary else None
		use_mp_hubbard_u = vasp_calculation_input_dictionary.pop('use_mp_hubbard_u') if 'use_mp_hubbard_u' in vasp_calculation_input_dictionary else None

		for file_path in [wavecar_path, chargecar_path]:
			if file_path != None and not Path.exists(file_path):
				print "Warning: Path " + str(file_path) + " specified does not exist. Not using."
				#raise Exception("Path " + str(file_path) + " specified does not exist.")

		if kpoints_scheme != None and kpoints_list != None:
			kpoints = Kpoints(scheme_string=kpoints_scheme, subdivisions_list=kpoints_list)

			if 'kspacing' in vasp_calculation_input_dictionary:
				raise Exception("kpoints are being specified by more than one method.")
		elif 'kspacing' not in vasp_calculation_input_dictionary:
			raise Exception("If kpoints aren't explicitly defined through a scheme and a list, the kspacing tag must be present in the incar.")
		else:
			kpoints = None

		potcar = Potcar(elements_list=information_structure.get_species_list(), calculation_type=potcar_type)


		submission_script_file = QueueAdapter.get_submission_file()

		if node_count == None:
			submission_script_file = QueueAdapter.modify_number_of_cores_from_num_atoms(submission_script_file, information_structure.site_count)
		else:
			submission_script_file = QueueAdapter.set_number_of_nodes(submission_script_file, node_count)

		submission_script_file = QueueAdapter.modify_submission_script(submission_script_file, modification_key=vasp_code_type)

		incar_modifiers = vasp_calculation_input_dictionary #whatever is left should only be incar modifiers - we popped all other keys

		for key, value in incar_modifiers.items(): #make sure there are no None values - these should not be put in INCAR
			if value in [None, 'None']:
				del incar_modifiers[key]

		if 'encut' in incar_modifiers and (0.1 < incar_modifiers['encut']) and (incar_modifiers['encut'] < 10.0): #Should use this as a multiplier times enmax
			enmax = potcar.get_enmax()

			incar_modifiers['encut'] = int(incar_modifiers['encut']*enmax)



		if incar_template == 'static':
			incar = IncarMaker.get_static_incar(custom_parameters_dictionary=incar_modifiers)
		elif incar_template == 'external_relaxation':
			incar = IncarMaker.get_external_relaxation_incar(custom_parameters_dictionary=incar_modifiers)
		elif incar_template != None:
			raise Exception("Incar template " + str(incar_template) + " not valid")
		else:
			incar = Incar()
			incar.modify_from_dictionary(incar_modifiers)

		if 'lreal' not in incar:
			if information_structure.site_count > 20:
				incar['lreal'] = 'Auto'
			else:
				incar['lreal'] = False

		if 'npar' not in incar:
			incar['npar'] = QueueAdapter.get_optimal_npar(submission_script_file)
		elif incar['npar'] in ['Remove', 'remove']:
			del incar['npar']

		###################TEMPORARILY HARDCODED FOR PEROVSKITES##########################################
		if use_mp_hubbard_u:
			u_species = initial_structure.get_species_list()[1]
			mp_hubbard_u_values = {'Co': 3.32, 'Cr': 3.7, 'Fe': 5.3, 'Mn': 3.9, 'Mo': 4.38, 'Ni': 6.2, 'V': 3.25, 'W': 6.2}

			if u_species in mp_hubbard_u_values.keys():

				u_value = mp_hubbard_u_values[u_species]

				incar['LDAU'] = True
				incar['LDAUJ'] = '0 0 0'
				incar['LDAUL'] = '0 2 0'
				incar['LDAUPRINT'] = 1
				incar['LDAUTYPE'] = 2
				incar['LDAUU'] = '0 ' + str(u_value) + ' 0'
				incar['LMAXMIX'] = 4
				incar['LORBIT'] = 11


		super(VaspCalculationGenerator, self).__init__(path=path, initial_structure=initial_structure, incar=incar, kpoints=kpoints, potcar=potcar, 
			submission_script_file=submission_script_file, contcar_path=contcar_path, wavecar_path=wavecar_path, chargecar_path=chargecar_path)
