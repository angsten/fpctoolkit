from fpctoolkit.structure_prediction.taylor_expansion.variable import Variable
from fpctoolkit.structure_prediction.taylor_expansion.expansion_term import ExpansionTerm
from fpctoolkit.structure_prediction.taylor_expansion.taylor_expansion import TaylorExpansion









strain_count = 6
displacement_count = 6


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