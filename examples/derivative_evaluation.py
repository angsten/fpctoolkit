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








a = 3.79
Nx = 1
Ny = 1
Nz = 1

vasp_run_inputs_dictionary = {
	'kpoint_scheme': 'Monkhorst',
	'kpoint_subdivisions_list': [4, 4, 4],
	'encut': 600
}


base_path = "./"

outcar = Outcar(Path.join(base_path, 'OUTCAR_small_refined'))
hessian = Hessian(outcar)



reference_structure=Perovskite(supercell_dimensions=[Nx, Ny, Nz], lattice=[[a*Nx, 0.0, 0.0], [0.0, a*Ny, 0.0], [0.0, 0.0, a*Nz]], species_list=['Sr', 'Ti', 'O'])


strain_count = 6
displacement_count = 2


variables = []


for i in range(strain_count):
	variables.append(Variable('strain', i))

for i in range(displacement_count):
	variables.append(Variable('displacement', i, centrosymmetry=True))

print "Variables list: " + '[' + ", ".join(str(variable) for variable in variables) + ']'



def term_acceptance_function(expansion_term):

	variables = expansion_term.get_active_variables()

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


perturbation_magnitudes_dictionary = {'strain': 0.01, 'displacement': 0.2}

de_path = Path.join(base_path, 'eval_test_4')

relaxation_path = Path.join(base_path, 'relaxation')


relaxation_input_dictionary= {
    'external_relaxation_count': 0,
    'kpoint_schemes_list': [vasp_run_inputs_dictionary['kpoint_scheme']],
    'kpoint_subdivisions_lists': [vasp_run_inputs_dictionary['kpoint_subdivisions_list']],
    'ediff': [0.0001],
    'encut': [vasp_run_inputs_dictionary['encut']]
}

relaxation = VaspRelaxation(path=relaxation_path, initial_structure=reference_structure, input_dictionary=relaxation_input_dictionary)


if not relaxation.complete:
	relaxation.update()
else:
	derivative_evaluator = DerivativeEvaluator(path=de_path, reference_structure=reference_structure, hessian=hessian, taylor_expansion=taylor_expansion, 
		reference_completed_vasp_relaxation_run=relaxation, vasp_run_inputs_dictionary=vasp_run_inputs_dictionary, perturbation_magnitudes_dictionary=perturbation_magnitudes_dictionary)

	derivative_evaluator.update()

	print derivative_evaluator.taylor_expansion