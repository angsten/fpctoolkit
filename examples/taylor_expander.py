
class Variable(object):

	def __init__(self, variable_type, variable_index, centrosymmetry=False):

		self.variable_type = variable_type
		self.variable_index = variable_index
		self.centrosymmetry = centrosymmetry

	def __str__(self):
		if self.variable_type == 'strain':
			type_string = 'eta'
		elif self.variable_type == 'mode':
			type_string = 'u'

		return type_string + '_' + str(self.variable_index+1)


class ExpansionTerm(object):

	def __init__(self, variables_list):
		self.variables_list = variables_list

		self.derivative_array = [0]*len(variables_list)

		self.coefficient = 0.0
		self.coefficient_string = '0.0'

	def update_derivatives_list(self, derivative_indices):
		for index in derivative_indices:
			self.derivative_array[index] += 1

		self.set_coefficient()


	def set_coefficient(self):
		order = self.get_order()
		non_zero_count = self.get_non_zero_count()

		if order == 1:
			self.coefficient = 1.0
		elif order == 2:
			if non_zero_count == 2:
				self.coefficient = 1.0
				self.coefficient_string = ''
			elif non_zero_count == 1:
				self.coefficient = 0.5
				self.coefficient_string = '1/2'
			else:
				raise Exception("bad count", non_zero_count, self.derivative_array)
		elif order == 3:
			if non_zero_count == 1:
				self.coefficient = 1.0/6.0
				self.coefficient_string = '1/6'
			elif non_zero_count == 2:
				self.coefficient = 1.0/3.0
				self.coefficient_string = '1/3'
			elif non_zero_count == 3:
				self.coefficient = 0.5
				self.coefficient_string = '1/2'
			else:
				raise Exception("bad count", non_zero_count, self.derivative_array)
		elif order == 4:
			if non_zero_count == 1:
				self.coefficient = 1.0/24.0
				self.coefficient_string = '1/24'
			elif non_zero_count == 2:
				self.coefficient = 1.0/12.0
				self.coefficient_string = '1/12'
			elif non_zero_count == 3:
				self.coefficient = 1.0/8.0
				self.coefficient_string = '1/8'
			elif non_zero_count == 4:
				self.coefficient = 1.0/6.0
				self.coefficient_string = '1/6'
			else:
				raise Exception("bad count", non_zero_count, self.derivative_array)

	def get_order(self):
		return sum(self.derivative_array)

	def get_non_zero_count(self):
		return len(filter(lambda x: x > 0, self.derivative_array))

	def __str__(self):
		if self.coefficient != 1.0:
			coefficient_string = '(' + self.coefficient_string + ')' + '*'
		else:
			coefficient_string = ''

		output_string = coefficient_string + 'f[' + ','.join(str(derivative_value) for derivative_value in self.derivative_array) + ']'

		for index, derivative_value in enumerate(self.derivative_array):

			if not derivative_value == 0:
				output_string += '*'

			if derivative_value == 1:
				output_string += str(self.variables_list[index])
			elif derivative_value == 2:
				output_string += str(self.variables_list[index]) + "^2"
			elif derivative_value == 3:
				output_string += str(self.variables_list[index]) + "^3"
			elif derivative_value == 4:
				output_string += str(self.variables_list[index]) + "^4"
		
		return output_string

	def is_pure_type(self, type_string):
		if type_string == 'mode':
			check_string = 'strain'
		elif type_string == 'strain':
			check_string = 'mode'

		for i, variable in enumerate(self.variables_list):
			if self.derivative_array[i] != 0 and variable.variable_type == check_string:
				return False

		return True

	def is_centrosymmetric(self):

		# print [str(variable) for variable in self.variables_list]
		number_of_odd_centrosymmetric_terms = 0

		for i, variable in enumerate(self.variables_list):
			if variable.centrosymmetry:
				if (self.derivative_array[i] % 2) == 1:
					number_of_odd_centrosymmetric_terms += 1

		# print self
		# print number_of_odd_centrosymmetric_terms
		# print "keep? ", not ((number_of_odd_centrosymmetric_terms % 2) == 1)					

		return ((number_of_odd_centrosymmetric_terms % 2) == 1)


class TaylorExpansion(object):

	def __init__(self, expansion_terms_instances_list):

		self.expansion_terms_list = expansion_terms_instances_list

	def __str__(self):
		return ' + '.join(str(expansion_term) for expansion_term in self.expansion_terms_list)

	def __len__(self):
		return len(self.expansion_terms_list)

	def remove_zero_terms_by_symmetry(self):

		remove_list = []

		for i, expansion_term in enumerate(self.expansion_terms_list):
			if expansion_term.is_centrosymmetric():
				remove_list.append(expansion_term)

		for expansion_term in remove_list:
			self.expansion_terms_list.remove(expansion_term)

	def remove_pure_strain_terms(self):
	
		remove_list = []

		for i, expansion_term in enumerate(self.expansion_terms_list):
			if expansion_term.is_pure_type('strain'):
				remove_list.append(expansion_term)

		for expansion_term in remove_list:
			self.expansion_terms_list.remove(expansion_term)		

	def remove_pure_mode_terms(self):
		remove_list = []

		for i, expansion_term in enumerate(self.expansion_terms_list):
			if expansion_term.is_pure_type('mode'):
				remove_list.append(expansion_term)

		for expansion_term in remove_list:
			self.expansion_terms_list.remove(expansion_term)				

remove_pure_strain_terms = True
remove_pure_mode_terms = False
remove_terms_by_symmetry = True
order = 2

strain_count = 0
mode_count = 6


variables = []


for i in range(strain_count):
	variables.append(Variable('strain', i+2))

for i in range(mode_count):
	variables.append(Variable('mode', i, centrosymmetry=True))

print "Variables list: " + '[' + ", ".join(str(variable) for variable in variables) + ']'


series_string = ''#'E0 + '


first_order_terms = []
for i, variable in enumerate(variables):
	expansion_term = ExpansionTerm(variables)

	expansion_term.update_derivatives_list([i])

	first_order_terms.append(expansion_term)


second_order_terms = []
if order > 1:
	for i in range(len(variables)):
		for j in range(i, len(variables)):
			expansion_term = ExpansionTerm(variables)

			expansion_term.update_derivatives_list([i, j])

			second_order_terms.append(expansion_term)

third_order_terms = []
if order > 2:
	for i in range(len(variables)):
		for j in range(i, len(variables)):
			for k in range(j, len(variables)):
				expansion_term = ExpansionTerm(variables)

				expansion_term.update_derivatives_list([i, j, k])

				second_order_terms.append(expansion_term)

fourth_order_terms = []

if order > 3:
	for i in range(len(variables)):
		for j in range(i, len(variables)):
			for k in range(j, len(variables)):
				for l in range(k, len(variables)):
					expansion_term = ExpansionTerm(variables)

					expansion_term.update_derivatives_list([i, j, k, l]) ########only add if all the same mode!

					second_order_terms.append(expansion_term)



all_terms_list = first_order_terms + second_order_terms + third_order_terms + fourth_order_terms

taylor_expansion = TaylorExpansion(all_terms_list)

if remove_terms_by_symmetry:
	taylor_expansion.remove_zero_terms_by_symmetry()

if remove_pure_strain_terms:
	taylor_expansion.remove_pure_strain_terms()

if remove_pure_mode_terms:
	taylor_expansion.remove_pure_mode_terms()

print
print "Number of terms:", len(taylor_expansion)


print '\n\t\t',
print taylor_expansion
print '\n'*3