#from fpctoolkit.io.vasp.vasp_calculation_generator import VaspCalculationGenerator

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
		'kpoints_scheme': 'Gamma',
		'kpoints_list': [6, 6, 4],
		'potcar_type': 'lda_paw',       #or 'gga_paw_pbe',
		'vasp_code_type': 'standard',   #or '100' for out-of-plane only relaxation
		'node_count': 2,                 #auto-set based on system size and host if not present

		'incar_template': 'static',      #if key not there, just creates a custom incar, can be 'static' or 'external_relaxation'
		'encut': 600,
		'ediff': 1e-6,
		'kspacing': 0.5,    #if this is specified, don't need kpoints info below
		'kgamma': True,
		'lreal': False,     #set based on system size if lreal key is not present,
		'npar': 4,          #must be 4 regardless of system size or:
		'npar': None, #npar will not be in incar no matter what or:
		#npar key not present (auto-set based on system size and host)
		#any other incar modifiers
	}
	"""

	def __init__(self, vasp_calculation_input_dictionary):

		vasp_calculation_input_dictionary = copy.deepcopy(vasp_calculation_input_dictionary)

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
		kpoints_list = vasp_calculation_input_dictionary.pop('kpoints_list') if 'kpoints_list' in vasp_calculation_input_dictionary else None
		potcar_type = vasp_calculation_input_dictionary.pop('potcar_type') if 'potcar_type' in vasp_calculation_input_dictionary else 'lda_paw'
		vasp_code_type = vasp_calculation_input_dictionary.pop('vasp_code_type') if 'vasp_code_type' in vasp_calculation_input_dictionary else 'standard'
		node_count = vasp_calculation_input_dictionary.pop('node_count') if 'node_count' in vasp_calculation_input_dictionary else None


		if kpoints_scheme != None and kpoints_list != None:
			kpoints = Kpoints(scheme_string=kpoints_scheme, subdivisions_list=kpoints_list)
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

		if incar_template == 'static':
			incar = IncarMaker.get_static_incar(custom_parameters_dictionary=incar_modifiers)
		elif incar_template == 'external_relaxation':
			incar = IncarMaker.get_external_relaxation_incar(custom_parameters_dictionary=incar_modifiers)
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
		elif incar['npar'] == None:
			del incar['npar']


		super(VaspCalculationGenerator, self).__init__(path=path, initial_structure=initial_structure, incar=incar, kpoints=kpoints, potcar=potcar, 
			submission_script_file=submission_script_file, contcar_path=contcar_path, wavecar_path=wavecar_path, chargecar_path=chargecar_path)
