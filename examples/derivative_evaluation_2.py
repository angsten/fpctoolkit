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



def get_taylor_expansion(number_of_strain_terms, number_of_displacement_terms, translational_mode_indices):

	variables = []


	for i in range(number_of_strain_terms):
		variables.append(Variable('strain', i))

	for i in range(number_of_displacement_terms):
		variables.append(Variable('displacement', i, centrosymmetry=True))

	print "Variables list: " + '[' + ", ".join(str(variable) for variable in variables) + ']'

	def term_acceptance_function(expansion_term):

		variables = expansion_term.get_active_variables()

		displacement_mode_indices = expansion_term.get_displacement_indices_list()

		for displacement_mode_index in displacement_mode_indices:
			if displacement_mode_index in translational_mode_indices:
				return False


		#remove all terms with in-plane strain variables in them - these are fixed to 0 for (100) epitaxy
		for variable in variables:
			if variable.type_string == 'strain' and variable.index in [0, 1, 5]:
				return False

		#assume no forces or stresses on the cell
		if expansion_term.order == 1: 
			return False

		#only expand to second order w.r.t. strain
		if expansion_term.is_pure_type('strain') and expansion_term.order > 2:
			return False

		#for perovskite structure under arbitrary homogeneous strain, displacement terms are centrosymmetric
		if expansion_term.is_centrosymmetric():
			return False

		#only go to fourth order in single variable dsiplacement terms - don't do fourth order cross terms
		if expansion_term.order == 4 and not expansion_term.has_single_variable():
			return False

		return True


	taylor_expansion = TaylorExpansion(variables_list=variables, term_acceptance_function=term_acceptance_function)

	print
	print "Number of terms:", len(taylor_expansion)


	print '\n\t\t',
	print taylor_expansion
	print '\n'*3

	return taylor_expansion



base_path = "./"




#######################################################################################################


number_of_strain_terms = 6
number_of_displacement_terms = 5 

#controls finite differences step size for evaluation of displacement second derivatives
displacement_finite_differrences_step_size = 0.04

#controls step size in plots
perturbation_magnitudes_dictionary = {'strain': 0.01, 'displacement': 0.04}


species_list = ['Sr', 'Ti', 'O']
a = 3.79
Nx = 2
Ny = 2
Nz = 2

ediff = 1e-6
encut = 600
kpoint_scheme = 'Monkhorst'
kpoint_subdivisions_list = [3, 3, 3]


#######################################################################################################


initial_relaxation_input_dictionary= {
    'external_relaxation_count': 3,
    'isif': [6],
    'kpoint_schemes_list': [kpoint_scheme],
    'kpoint_subdivisions_lists': [kpoint_subdivisions_list],
    'ediff': [1e-4, 1e-6, 1e-8],
    'encut': [encut],
    'submission_script_modification_keys_list': ['100'],
    'lwave': [True],
    'lreal': [False],
    'addgrid': [True]
}

dfpt_incar_settings = {
	'encut': encut,
	'ediff': 1e-8
}

derivative_evaluation_vasp_run_inputs_dictionary = {
	'kpoint_scheme': kpoint_scheme,
	'kpoint_subdivisions_list': kpoint_subdivisions_list,
	'submission_node_count': 1,
	'encut': encut,
	'ediff': ediff,
	'lreal': False,
	'addgrid': True,
	'symprec': 1e-6
}

minima_relaxation_input_dictionary = {
    'external_relaxation_count': 3,
    'kpoint_schemes_list': [kpoint_scheme],
    'kpoint_subdivisions_lists': [kpoint_subdivisions_list],
    'submission_node_count': 1,
    'potim': [0.1, 0.2, 0.4],
    'isif': [21, 71, 161],
    'ediff': [1e-4, 1e-5, 1e-6],
    'encut': [encut],
    'submission_script_modification_keys_list': ['100'],
    'lwave': [True],
    'lreal': [False],
    'addgrid': [True]
}


initial_structure=Perovskite(supercell_dimensions=[Nx, Ny, Nz], lattice=[[a*Nx, 0.0, 0.0], [0.0, a*Ny, 0.0], [0.0, 0.0, a*Nz*1.02]], species_list=species_list)


relaxation = VaspRelaxation(path=Path.join(base_path, 'relaxation'), initial_structure=initial_structure, input_dictionary=initial_relaxation_input_dictionary)


if not relaxation.complete:
	relaxation.update()
else:
	
	relaxed_structure = relaxation.final_structure


	force_calculation_path = Path.join(base_path, 'dfpt_force_calculation')

	kpoints = Kpoints(scheme_string=kpoint_scheme, subdivisions_list=kpoint_subdivisions_list)
	incar = IncarMaker.get_dfpt_hessian_incar(dfpt_incar_settings)
	input_set = VaspInputSet(relaxed_structure, kpoints, incar, auto_change_lreal=False, auto_change_npar=False)

	dfpt_force_run = VaspRun(path=force_calculation_path, input_set=input_set)

	if not dfpt_force_run.complete:
		dfpt_force_run.update()


	else:

		hessian = Hessian(dfpt_force_run.outcar)
		#hessian.print_eigen_components()
		hessian.print_eigenvalues()

		taylor_expansion = get_taylor_expansion(number_of_strain_terms, number_of_displacement_terms, hessian.translational_mode_indices)


		print ''.join(initial_structure.get_species_list()) + '3' + ' a=' + str(a) + 'A ediff=' + str(ediff) + ' encut=' + str(encut) + ' ' + 'x'.join(str(k) for k in kpoint_subdivisions_list) + kpoint_scheme[0] + ' disp_step=' + str(displacement_finite_differrences_step_size) + 'A',


		de_path = Path.join(base_path, 'term_coefficient_calculations')
		derivative_evaluator = DerivativeEvaluator(path=de_path, reference_structure=relaxed_structure, hessian=hessian, taylor_expansion=taylor_expansion, 
			reference_completed_vasp_relaxation_run=relaxation, vasp_run_inputs_dictionary=derivative_evaluation_vasp_run_inputs_dictionary, 
			perturbation_magnitudes_dictionary=perturbation_magnitudes_dictionary, displacement_finite_differrences_step_size=displacement_finite_differrences_step_size)

		derivative_evaluator.update()

		print
		print derivative_evaluator.taylor_expansion







		guessed_minima_data_path = Path.join(base_path, 'guessed_chromosomes')
		minima_path = Path.join(base_path, 'minima_tests')


		if Path.exists(guessed_minima_data_path):

			minima_file = File(guessed_minima_data_path)

			eigen_chromosome_energy_pairs_list = [] #[[predicted_energy_difference_1, [e1, e2, e3, e4, ...]], [predicted_energy_difference_2, [e1, ...]]]

			for line in minima_file:
				energy_difference = float((line.strip()).split(',')[0])
				eigen_chromosome = [float(x) for x in (line.strip()).split(',')[1].split(' ')[1:]]


				eigen_chromosome_energy_pairs_list.append([energy_difference, eigen_chromosome])

			minima_relaxer = MinimaRelaxer(path=minima_path, reference_structure=relaxed_structure, reference_completed_vasp_relaxation_run=relaxation, hessian=hessian, 
				vasp_relaxation_inputs_dictionary=minima_relaxation_input_dictionary, eigen_chromosome_energy_pairs_list=eigen_chromosome_energy_pairs_list)
