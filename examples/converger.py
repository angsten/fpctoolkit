import copy

from fpctoolkit.structure.structure import Structure
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.util.path import Path






"""
Script that converges a system with respect to encut, kpoints or ediff.
"""



def get_structure_list(path):
	"""loads in poscars at path and returns list of structures"""

	path = Path.clean(path)
	files = Path.get_list_of_files_at_path(path)
	structs = []

	for file in files:
		structs.append(Structure(Path.join(path, file)))

	return structs



def converge(base_path, structures_list, calculation_set_input_dictionary_template, change_set):

	Path.make(base_path)

	for structure_count, structure in enumerate(structures_list):
		structure_path = Path.join(base_path, 'structure_'+str(structure_count))

		Path.make(structure_path)

		change_key = change_set[0]
		change_values_list = change_set[1]
		num_relaxations = len(change_values_list)


		for run_set_count, change_set_value in enumerate(change_values_list):
			relaxation_set_path = Path.join(structure_path, 'relaxation_set_'+str(run_set_count))

			inputs = copy.deepcopy(calculation_set_input_dictionary_template)
			inputs[change_key] = change_set_value

			vasp_relaxation = VaspRelaxation(path=relaxation_set_path, initial_structure=structure, input_dictionary=inputs)

			vasp_relaxation.update()

			if vasp_relaxation.complete:
				print change_key, change_set_value, vasp_relaxation.get_final_energy(per_atom=True), vasp_relaxation.total_time


if __name__ == "__main__":

    print "\n"*5



    structures_list = get_structure_list('./structures')

	calculation_set_input_dictionary = {
		'external_relaxation_count': 0,
		'kpoint_schemes_list': ['Monkhorst'],
		'kpoint_subdivisions_lists': [[2, 2, 2]],
		'submission_script_modification_keys_list': ['100'],
		'submission_node_count_list': [1],
		'ediff': [0.000001],
		'encut': [800]
	}

	#######encut###################################################################################

	encuts_change_lists = [[300], [400]]#, [500], [600], [700], [800]]
	change_set = ('encut', encuts_change_lists)
	convergence_path = './encut_convergence'

	print convergence_path

    converge(base_path=convergence_path, structures_list=structures_list, calculation_set_input_dictionary_template=calculation_set_input_dictionary, change_set=change_set)



	#######kpoints###################################################################################

	kpoints_change_lists = [[[1, 1, 1]], [[2, 2, 2]], [[3, 3, 3]], [[4, 4, 4]]]
	change_set = ('kpoint_subdivisions_lists', kpoints_change_lists)
	convergence_path = './kpoint_convergence'

	print convergence_path

	converge(base_path=convergence_path, structures_list=structures_list, calculation_set_input_dictionary_template=calculation_set_input_dictionary, change_set=change_set)
