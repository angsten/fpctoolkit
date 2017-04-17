import fpctoolkit.util.phonopy_interface.phonopy_utility as phonopy_utility

from fpctoolkit.workflow.vasp_phonon import VaspPhonon

from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.util.path import Path




supercell_dimensions = [2, 2, 2]
base_path = './cubic_BaTiO3_' + "_".join(str(dimension) for dimension in supercell_dimensions)





relaxation_path = Path.join(base_path, 'relaxation')
phonon_path = Path.join(base_path, 'phonons')

Path.make(base_path)

phonopy_inputs_dictionary = {
	'supercell_dimensions': supercell_dimensions,
	'symprec': 0.0001,
	'displacement_distance': 0.01,
	'nac': True
	}

vasp_run_inputs_dictionary = {
	'kpoint_scheme': 'Monkhorst',
	'kpoint_subdivisions_list': [4, 4, 4],
	'encut': 800
	}

relax_input_dictionary = {
	'external_relaxation_count': 3,
	'kpoint_schemes_list': [vasp_run_inputs_dictionary['kpoint_scheme']],
	'kpoint_subdivisions_lists': [[vasp_run_inputs_dictionary['kpoint_subdivisions_list'][i]*phonopy_inputs_dictionary['supercell_dimensions'][i] for i in range(3)]],
	#'submission_script_modification_keys_list': ['100'],
	#'submission_node_count_list': [1],
	'potim': [0.05, 0.2, 0.4],
	'ediff': [0.000001, 0.00000001, 0.00000000001],
	'encut': [vasp_run_inputs_dictionary['encut']]
	}

initial_structure=Perovskite(supercell_dimensions=[1, 1, 1], lattice=[[4.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 4.0]], species_list=['Ba', 'Ti', 'O'])



relax = vasp_relaxation = VaspRelaxation(path=relaxation_path, initial_structure=initial_structure, input_dictionary=relax_input_dictionary)

relax.update()


if relax.complete:
	relaxed_structure = relax.final_structure

	vasp_phonon_calculation = VaspPhonon(path=phonon_path, initial_structure=relaxed_structure, phonopy_inputs_dictionary=phonopy_inputs_dictionary, vasp_run_inputs_dictionary=vasp_run_inputs_dictionary)
