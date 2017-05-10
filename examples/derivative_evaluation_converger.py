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


strain_count = 6
displacement_count = 2

convergence_terms_list = [[0, 0, 0, 0, 0, 0, 2, 0],
						  [0, 0, 0, 0, 0, 0, 0, 2]]


displacement_magnitudes_list = [0.005, 0.01, 0.05, 0.1, 0.2, 0.5]


variables = []


for i in range(strain_count):
	variables.append(Variable('strain', i))

for i in range(displacement_count):
	variables.append(Variable('displacement', i, centrosymmetry=True))

print "Variables list: " + '[' + ", ".join(str(variable) for variable in variables) + ']'



def term_acceptance_function(expansion_term):
	if expansion_term.derivative_array in convergence_terms_list:
		return True
	else:
		return False


taylor_expansion = TaylorExpansion(variables_list=variables, term_acceptance_function=term_acceptance_function)

print
print "Number of terms:", len(taylor_expansion)


print '\n\t\t',
print taylor_expansion
print '\n'*3




base_path = "./"




a = 3.79
Nx = 1
Ny = 1
Nz = 1

vasp_run_inputs_dictionary = {
	'kpoint_scheme': 'Monkhorst',
	'kpoint_subdivisions_list': [8, 8, 8],
	'encut': 900,
	'ediff': 1e-9,
	'lreal': False,
	'addgrid': True
}

relaxation_input_dictionary= {
    'external_relaxation_count': 3,
    'isif': [6],
    'kpoint_schemes_list': [vasp_run_inputs_dictionary['kpoint_scheme']],
    'kpoint_subdivisions_lists': [vasp_run_inputs_dictionary['kpoint_subdivisions_list']],
    'ediff': [0.00001, 1e-7, 1e-9],
    'encut': [vasp_run_inputs_dictionary['encut']],
    'submission_script_modification_keys_list': ['100'],
    'lwave': [True]
}


initial_structure=Perovskite(supercell_dimensions=[Nx, Ny, Nz], lattice=[[a*Nx, 0.0, 0.0], [0.0, a*Ny, 0.0], [0.0, 0.0, a*Nz*1.02]], species_list=['Sr', 'Ti', 'O'])


relaxation = VaspRelaxation(path=Path.join(base_path, 'relaxation'), initial_structure=initial_structure, input_dictionary=relaxation_input_dictionary)


if not relaxation.complete:
	relaxation.update()
else:
	
	relaxed_structure = relaxation.final_structure

	force_calculation_path = Path.join(base_path, 'dfpt_force_calculation')

	kpoints = Kpoints(scheme_string=vasp_run_inputs_dictionary['kpoint_scheme'], subdivisions_list=vasp_run_inputs_dictionary['kpoint_subdivisions_list'])
	incar = IncarMaker.get_dfpt_hessian_incar({'encut': vasp_run_inputs_dictionary['encut']})

	input_set = VaspInputSet(relaxed_structure, kpoints, incar, auto_change_lreal=False, auto_change_npar=False)

	dfpt_force_run = VaspRun(path=force_calculation_path, input_set=input_set)

	if not dfpt_force_run.complete:
		dfpt_force_run.update()
	else:

		hessian = Hessian(dfpt_force_run.outcar)
		hessian.print_eigen_components()


		derivative_evaluator_list = []
		for i in range(len(displacement_magnitudes_list)):

			perturbation_magnitudes_dictionary = {'strain': 0.01, 'displacement': displacement_magnitudes_list[i]}

			de_path = Path.join(base_path, 'term_coefficient_calculations_' + str(displacement_magnitudes_list[i]))
			derivative_evaluator = DerivativeEvaluator(path=de_path, reference_structure=relaxed_structure, hessian=hessian, taylor_expansion=taylor_expansion, 
				reference_completed_vasp_relaxation_run=relaxation, vasp_run_inputs_dictionary=vasp_run_inputs_dictionary, perturbation_magnitudes_dictionary=perturbation_magnitudes_dictionary)

			derivative_evaluator.update()

			derivative_evaluator_list.append(derivative_evaluator)	


		for i in range(len(derivative_evaluator_list[0].taylor_expansion.expansion_terms_list)):
			print '\n' + derivative_evaluator_list[0].taylor_expansion.expansion_terms_list[i]

			for j, derivative_evaluator in enumerate(derivative_evaluator_list):

				print displacement_magnitudes_list[j], derivative_evaluator.taylor_expansion.expansion_terms_list[i].derivative_coefficient

		