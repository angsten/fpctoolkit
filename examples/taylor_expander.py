
class Variable(object):

	def __init__(self, variable_type, variable_index):

		self.variable_type = variable_type
		self.variable_index = variable_index

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
			elif derivative_value == 3:
				output_string += str(self.variables_list[index]) + "^4"
		
		return output_string




strain_count = 1
mode_count = 0


variables = []


for i in range(strain_count):
	variables.append(Variable('strain', i))

for i in range(mode_count):
	variables.append(Variable('mode', i))

print "Variables list: " + '[' + ", ".join(str(variable) for variable in variables) + ']'


series_string = 'E0 + '


first_order_terms = []
for i, variable in enumerate(variables):
	expansion_term = ExpansionTerm(variables)

	expansion_term.update_derivatives_list([i])

	first_order_terms.append(expansion_term)


second_order_terms = []
for i in range(len(variables)):
	for j in range(i, len(variables)):
		expansion_term = ExpansionTerm(variables)

		expansion_term.update_derivatives_list([i, j])

		second_order_terms.append(expansion_term)

third_order_terms = []
for i in range(len(variables)):
	for j in range(i, len(variables)):
		for k in range(j, len(variables)):
			expansion_term = ExpansionTerm(variables)

			expansion_term.update_derivatives_list([i, j, k])

			second_order_terms.append(expansion_term)

fourth_order_terms = []
for i in range(len(variables)):
	for j in range(i, len(variables)):
		for k in range(j, len(variables)):
			expansion_term = ExpansionTerm(variables)

			expansion_term.update_derivatives_list([i, j, k])

			second_order_terms.append(expansion_term)



all_terms_list = first_order_terms + second_order_terms + third_order_terms

series_string += ' + '.join(str(expansion_term) for expansion_term in all_terms_list)

















print '\n\t\t',
print series_string
print '\n'*3