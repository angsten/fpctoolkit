from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.io.vasp.outcar import Outcar
from fpctoolkit.phonon.eigen_structure import EigenStructure
from fpctoolkit.structure_prediction.taylor_expansion.variable import Variable
from fpctoolkit.structure_prediction.taylor_expansion.expansion_term import ExpansionTerm
from fpctoolkit.structure_prediction.taylor_expansion.taylor_expansion import TaylorExpansion
from fpctoolkit.structure_prediction.taylor_expansion.derivative_evaluator import DerivativeEvaluator
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.util.path import Path
from fpctoolkit.phonon.hessian import Hessian
from fpctoolkit.structure.structure import Structure
from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.structure_prediction.taylor_expansion.minima_relaxer import MinimaRelaxer
from fpctoolkit.io.file import File
from fpctoolkit.workflow.epitaxial_relaxer import EpitaxialRelaxer
import sys


def run_misfit_strain(path, misfit_strain, input_dictionary, initial_relaxation_input_dictionary, dfpt_incar_settings, derivative_evaluation_vasp_run_inputs_dictionary, minima_relaxation_input_dictionary,
		      epitaxial_relaxation_input_dictionary):

	Path.make(path)
	guessed_minima_data_path = Path.join(path, 'guessed_chromosomes')

	species_list = input_dictionary['species_list']
	reference_lattice_constant = input_dictionary['reference_lattice_constant']
	Nx = input_dictionary['supercell_dimensions_list'][0]
	Ny = input_dictionary['supercell_dimensions_list'][1]
	Nz = input_dictionary['supercell_dimensions_list'][2]	
	displacement_finite_differences_step_size = input_dictionary['displacement_finite_differences_step_size']	
	perturbation_magnitudes_dictionary = input_dictionary['perturbation_magnitudes_dictionary']

	a = reference_lattice_constant*(1.0+misfit_strain)

	
	initial_structure=Perovskite(supercell_dimensions=[Nx, Ny, Nz], lattice=[[a*Nx, 0.0, 0.0], [0.0, a*Ny, 0.0], [0.0, 0.0, reference_lattice_constant*Nz*(1.0+0.3*(1.0-(a/reference_lattice_constant)))]], species_list=species_list)
	relaxation = VaspRelaxation(path=Path.join(path, 'relaxation'), initial_structure=initial_structure, input_dictionary=initial_relaxation_input_dictionary)

	if not relaxation.complete:
		relaxation.update()
		return False

	relaxed_structure = relaxation.final_structure

	relaxed_structure_path = Path.join(path, 'output_relaxed_structure')
	relaxed_structure.to_poscar_file_path(relaxed_structure_path)



	
	force_calculation_path = Path.join(path, 'dfpt_force_calculation')

	kpoints = Kpoints(scheme_string=kpoint_scheme, subdivisions_list=kpoint_subdivisions_list)
	incar = IncarMaker.get_dfpt_hessian_incar(dfpt_incar_settings)
	input_set = VaspInputSet(relaxed_structure, kpoints, incar, auto_change_lreal=False, auto_change_npar=False)
	
	dfpt_force_run = VaspRun(path=force_calculation_path, input_set=input_set)

	if not dfpt_force_run.complete:
		dfpt_force_run.update()
		return False
	
	hessian = Hessian(dfpt_force_run.outcar)

	if input_dictionary['write_hessian_data']:
		hessian.print_eigenvalues_to_file(Path.join(path, 'output_eigen_values'))
		hessian.print_eigen_components_to_file(Path.join(path, 'output_eigen_components'))
		hessian.print_mode_effective_charge_vectors_to_file(Path.join(path, 'output_mode_effective_charge_vectors'), relaxed_structure)


		eigen_structure = EigenStructure(reference_structure=relaxed_structure, hessian=hessian)

		mode_structures_path = Path.join(path, 'mode_rendered_structures')
		Path.make(mode_structures_path)

		sorted_eigen_pairs = hessian.get_sorted_hessian_eigen_pairs_list()
		for i, structure in enumerate(eigen_structure.get_mode_distorted_structures_list(amplitude=0.6)):
			if i > 30:
				break
			structure.to_poscar_file_path(Path.join(mode_structures_path, 'u'+str(i+1)+'_'+str(round(sorted_eigen_pairs[i].eigenvalue, 2))+'.vasp'))

	#sys.exit()

	
	if not Path.exists(guessed_minima_data_path):
		variable_specialty_points_dictionary = input_dictionary['variable_specialty_points_dictionary_set'][misfit_strain] if input_dictionary.has_key(misfit_strain) else {}

		derivative_evaluation_path = Path.join(path, 'expansion_coefficient_calculations')
		derivative_evaluator = DerivativeEvaluator(path=derivative_evaluation_path, reference_structure=relaxed_structure, hessian=hessian, reference_completed_vasp_relaxation_run=relaxation,
							   vasp_run_inputs_dictionary=derivative_evaluation_vasp_run_inputs_dictionary, perturbation_magnitudes_dictionary=perturbation_magnitudes_dictionary,
							   displacement_finite_differences_step_size=displacement_finite_differences_step_size, status_file_path=Path.join(path, 'output_derivative_plot_data'),
							   variable_specialty_points_dictionary=variable_specialty_points_dictionary)

		derivative_evaluator.update()


	else:			
		minima_path = Path.join(path, 'minima_relaxations')

		minima_relaxer = MinimaRelaxer(path=minima_path, reference_structure=relaxed_structure, reference_completed_vasp_relaxation_run=relaxation, hessian=hessian, 
					       vasp_relaxation_inputs_dictionary=minima_relaxation_input_dictionary, eigen_chromosome_energy_pairs_file_path=guessed_minima_data_path, max_minima=input_dictionary['max_minima'])
		
		minima_relaxer.update()
		minima_relaxer.print_status_to_file(Path.join(path, 'output_minima_relaxations_status'))
		
		if minima_relaxer.complete:
			#minima_relaxer.print_selected_uniques_to_file(file_path=Path.join(path, 'output_selected_unique_minima_relaxations'))
			sorted_uniques = minima_relaxer.get_sorted_unique_relaxation_data_list()

			return sorted_uniques
		



if __name__ == '__main__':

	#######################################################################################################

	input_dictionary = {}
	input_dictionary['species_list'] = File('./system_formula')[0].strip().split(' ')
	print input_dictionary['species_list']


	#which misfit strains to run expansion approximation scheme at 
	misfit_strains_list = [-0.02, -0.01, 0.0, 0.01, 0.02]

	variable_specialty_points_dictionary_set = {}
	#variable_specialty_points_dictionary_set[-0.02] = {
	#	'u_2': [0.001, 0.2],
	#	'e_3': [0.45]
	#	}

	lattice_constants_dictionary = {}
	lattice_constants_dictionary['SrTiO'] = 3.8610547
	lattice_constants_dictionary['CaTiO'] = 3.81331597
	lattice_constants_dictionary['SrHfO'] = 4.0680851
	lattice_constants_dictionary['KVO'] = 3.75

	
	input_dictionary['reference_lattice_constant'] = lattice_constants_dictionary["".join(input_dictionary['species_list'])]
	input_dictionary['supercell_dimensions_list'] = [2, 2, 2]
	input_dictionary['variable_specialty_points_dictionary_set'] = variable_specialty_points_dictionary_set

	
	#controls finite differences step size for evaluation of displacement second derivatives
	input_dictionary['displacement_finite_differences_step_size'] = 0.04

	#controls step size in plots
	input_dictionary['perturbation_magnitudes_dictionary'] = {'strain': 0.005, 'displacement': 0.05}


	ediff = 1e-7
	dfpt_ediff = 1e-9
	encut = 600
	kpoint_scheme = 'Monkhorst'
	kpoint_subdivisions_list = [3, 3, 3]

	#max number of minima relaxations to perform. Set to None to relax all guessed minima.
	input_dictionary['max_minima'] = 6
	input_dictionary['write_hessian_data'] = True

	#controls which misfit strains to apply to the minima structures when constructing the final phase diagram
	epitaxial_relaxations_misfit_strains_list = [-0.02, -0.015, -0.01, -0.005, 0.0, 0.005, 0.01, 0.015, 0.02]
	calculate_polarizations = False
	update_eptiaxy_only = False

	#######################################################################################################

	#base_path = Path.join("./", "".join(input_dictionary['species_list']) + "3")
	base_path = './'
	expansion_path = Path.join(base_path, 'expansions')
	epitaxial_path = Path.join(base_path, 'epitaxial_relaxations')

	Path.make(expansion_path)


	
	initial_relaxation_input_dictionary= {
	    'external_relaxation_count': 3,
	    'isif': [6],
	    'kpoint_schemes_list': [kpoint_scheme],
	    'kpoint_subdivisions_lists': [kpoint_subdivisions_list],
	    'ediff': [1e-4, 1e-6, 1e-8],
	    'encut': [encut],
	    'submission_node_count_list': [1],
	    'submission_script_modification_keys_list': ['100'],
	    'lwave': [True],
	    'lreal': [False],
	    'addgrid': [True]
	}

	dfpt_incar_settings = {
		'encut': encut,
		'ediff': dfpt_ediff
	}

	derivative_evaluation_vasp_run_inputs_dictionary = {
		'kpoint_scheme': kpoint_scheme,
		'kpoint_subdivisions_list': kpoint_subdivisions_list,
		#'submission_node_count': 1,
		'encut': encut,
		'ediff': ediff,
		'lreal': False,
		'addgrid': True,
		'symprec': 1e-7
	}

	minima_relaxation_input_dictionary = {
	    'external_relaxation_count': 3,
	    'kpoint_schemes_list': [kpoint_scheme],
	    'kpoint_subdivisions_lists': [kpoint_subdivisions_list],
	    'ediff': [1e-4, 1e-5, 1e-6],
	    'encut': [encut],
	    'submission_script_modification_keys_list': ['100'],
	    'lreal': [False],
	    'potim': [0.2, 0.3, 0.4],
	    'nsw': [21, 71, 161],
	    'addgrid': [True]
	}

	epitaxial_relaxation_input_dictionary = {
	    'external_relaxation_count': 4,
	    'kpoint_schemes_list': [kpoint_scheme],
	    'kpoint_subdivisions_lists': [kpoint_subdivisions_list],
	    'ediff': [1e-5, 1e-6, 1e-7, 1e-7],
	    'encut': [encut],
	    'submission_script_modification_keys_list': ['100'],
	    'lwave': [True],
	    'lreal': [False],
	    'potim': [0.2, 0.3, 0.4],
	    'nsw': [21, 71, 161],
	    'addgrid': [True],
	    'symprec': [1e-7]
	}

	initial_epitaxial_structures_list = []

	if not update_eptiaxy_only:
		for misfit_strain in misfit_strains_list:
			print "Misfit strain: " + str(misfit_strain)

			run_path = Path.join(expansion_path, str(misfit_strain).replace('-', 'n'))
			
			sorted_unique_triplets = run_misfit_strain(path=run_path, misfit_strain=misfit_strain, input_dictionary=input_dictionary, initial_relaxation_input_dictionary=initial_relaxation_input_dictionary,
					  dfpt_incar_settings=dfpt_incar_settings, derivative_evaluation_vasp_run_inputs_dictionary=derivative_evaluation_vasp_run_inputs_dictionary,
					  minima_relaxation_input_dictionary=minima_relaxation_input_dictionary, epitaxial_relaxation_input_dictionary=epitaxial_relaxation_input_dictionary)
				
			if sorted_unique_triplets:
				curtailed_sorted_triplets = [sorted_unique_triplets[0]] ##########################################################only selecting lowest energy for now		
				initial_epitaxial_structures_list += [data_triplet[0].final_structure for data_triplet in curtailed_sorted_triplets]



		sys.exit('\n\n**exiting before epitaxial relaxation**\n\n')

	#for now, just arrange super list of [relaxation, chromosome] and print out energy and first few of chromosome - inspect these to see how diverse they are, sort by energy first

	#maybe don't run this until all structures have been determined
	if (len(initial_epitaxial_structures_list) > 0) or update_eptiaxy_only:
		print "Updating Epitaxial Relaxations"

		Path.make(epitaxial_path)

		a = 1.0 #doesn't matter
		Nx = input_dictionary['supercell_dimensions_list'][0]
		Ny = input_dictionary['supercell_dimensions_list'][1]
		Nz = input_dictionary['supercell_dimensions_list'][2]	

		reference_structure=Perovskite(supercell_dimensions=[Nx, Ny, Nz], lattice=[[a*Nx, 0.0, 0.0], [0.0, a*Ny, 0.0], [0.0, 0.0, a]], species_list=input_dictionary['species_list'])

		epitaxial_relaxer = EpitaxialRelaxer(path=epitaxial_path, initial_structures_list=initial_epitaxial_structures_list, reference_structure=reference_structure, vasp_relaxation_inputs_dictionary=epitaxial_relaxation_input_dictionary, 
			reference_lattice_constant=input_dictionary['reference_lattice_constant'], misfit_strains_list=epitaxial_relaxations_misfit_strains_list, supercell_dimensions_list=input_dictionary['supercell_dimensions_list'],
			calculate_polarizations=calculate_polarizations)
		
		epitaxial_relaxer.update()

		for data_dictionary in epitaxial_relaxer.get_data_dictionaries_list():
			for key in data_dictionary.get_keys():
				print data_dictionary[key]
			print