import fpctoolkit.util.phonopy_interface.phonopy_utility as phonopy_utility

from fpctoolkit.workflow.vasp_phonon import VaspPhonon

from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.util.path import Path
import fpctoolkit.util.phonopy_interface.phonopy_utility as phonopy_utility
from fpctoolkit.phonon.phonon_structure import PhononStructure

from fpctoolkit.phonon.normal_mode import NormalMode




supercell_dimensions = [2, 2, 2]
base_path = './'

phonopy_inputs_dictionary = {
	'supercell_dimensions': supercell_dimensions,
	'symprec': 0.0001,
	'displacement_distance': 0.01,
	'nac': False
	}

vasp_run_inputs_dictionary = {
	'kpoint_scheme': 'Monkhorst',
	'kpoint_subdivisions_list': [4, 4, 4],
	'encut': 600
	}

init_struct_path = Path.join(base_path, 'initial_structure')
force_constants_path = Path.join(base_path, 'FORCE_CONSTANTS')
initial_structure = Structure(init_struct_path)

phonon = phonopy_utility.get_initialized_phononopy_instance(initial_structure, phonopy_inputs_dictionary, force_constants_path)

relax_input_dictionary = {
	'external_relaxation_count': 0,
	'kpoint_schemes_list': [vasp_run_inputs_dictionary['kpoint_scheme']],
	'kpoint_subdivisions_lists': [vasp_run_inputs_dictionary['kpoint_subdivisions_list']],
	'submission_node_count_list': [1],
	'ediff': [0.00001],
	'encut': [vasp_run_inputs_dictionary['encut']]
	}

q_points_list = [(0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.0, 0.5, 0.0), (0.0, 0.0, 0.5), (0.5, 0.5, 0.0), (0.5, 0.0, 0.5), (0.0, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, 0.5)]

pbs = phonopy_utility.get_phonon_band_structure_instance(phonopy_instance=phonon, q_points_list=q_points_list)


coordinate_indices = [180, 0, 211, 23, 8, 122, 11]


for coordinate_index in coordinate_indices:

	ps = PhononStructure(primitive_cell_structure=pbs.primitive_cell_structure, phonon_band_structure=pbs, supercell_dimensions_list=phonopy_inputs_dictionary['supercell_dimensions'])

	coordinate_path = Path.join(base_path, "coordinate_index_" + str(coordinate_index))
		
	Path.make(coordinate_path)

	print "Coordinate index is " + str(coordinate_index) + ", Frequency squared is " + str(ps.normal_coordinates_list[coordinate_index].frequency**2)

	for i in range(4):
		relaxation_path = Path.join(coordinate_path, str(i))
		
		ps.normal_coordinates_list[coordinate_index].coefficient = i*0.1

		dist_struct = ps.get_distorted_supercell_structure()


		relax = vasp_relaxation = VaspRelaxation(path=relaxation_path, initial_structure=dist_struct, input_dictionary=relax_input_dictionary)

		relax.update()


		if relax.complete:
			relaxed_structure = relax.final_structure

			print str(ps.normal_coordinates_list[coordinate_index].coefficient), relax.get_final_energy()