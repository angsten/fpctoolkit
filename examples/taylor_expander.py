
class Variable(object):
	"""
	A variable as part of a taylor expansion. Has a type string and index integer.
	"""

	def __init__(self, type_string, variable_index, centrosymmetry=False):
		"""
		Variable type can be displacement or strain. The index should denote which strain or displacement variable this is by an index.
		"""

		self.value = 0.0
		self.type_string = type_string
		self.variable_index = variable_index
		self.centrosymmetry = centrosymmetry

	def __str__(self):
		if self.type_string == 'strain':
			type_string = 'e'
		elif self.type_string == 'displacement':
			type_string = 'u'

		return type_string + '_' + str(self.variable_index+1)




class ExpansionTerm(object):
	"""
	A term in a taylor expansion like (1/2)*f[2,0,0,0,0,0]*u_1^2. The first part is the term coefficient (fixed), the second is the derivative_coefficient (either known or unknown), and
	the last part is the variable and its order (second order in this case).

	f[0,1,0,0,0,1]*u_2*u_6 is an example term with two variables.

	self.derivative_array holds the list of derivative orders. f[0,1,0,0,0,1] means first derivatives are taken w.r.t. the second and sixth variables in the term.
	"""

	def __init__(self, variables_list):
		"""
		Variables list should be a list of ALL Variable instances of the total taylor expansion that are initialized already. That is, the list should contain more than just the variables in this term.
		"""

		self.variables_list = variables_list

		self.derivative_array = [0]*len(variables_list)

		self.derivative_coefficient_value = 0.0

		self.coefficient = 0.0
		self.coefficient_string = '0.0'

	def update_derivatives_list(self, derivative_indices_list):
		"""
		For each index in derivative_indices_list, the corresponding self.derivative_array component is incremented by one. 
		For example:

		update_derivatives_list([1, 4]) means f[0, 0, 0, 0, 0] => f[0, 1, 0, 0, 1]
		"""
		for index in derivative_indices_list:
			self.derivative_array[index] += 1

		self.set_coefficient()


	def set_coefficient(self):
		"""
		Determine, based on what order of a derivative this is, what the taylor expansion coefficient is for this term.
		"""

		order = self.order
		non_zero_count = self.get_non_zero_count() #number of variables with non-zero derivatives.

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

	@property
	def order(self):
		"""
		Get this term's order. e.g., f[0,0,1,0,0,1]*u_3*u_6 is second order
		"""

		return sum(self.derivative_array)

	def get_non_zero_count(self):
		"""
		Returns the number of variables with non-zero derivatives in this term. f[0,0,1,0,0,1]*u_3*u_6 has two non-zero derivatives.
		"""

		return len(filter(lambda x: x > 0, self.derivative_array))


	def is_pure_type(self, type_string):
		"""
		Returns true if all variables in the term are of type type_string
		"""

		for i, variable in enumerate(self.variables_list):
			if self.derivative_array[i] != 0 and variable.type_string != type_string:
				return False

		return True

	def is_centrosymmetric(self):
		"""
		Retruns true if this term must be zero based on the centrosymmetry of its variables. That is, if there is an odd number of variables a_i in this term which obey
		f[a_i] = f[-a_i], then the derivative for this term must be zero by symmetry.
		"""

		number_of_centrosymmetric_terms = 0

		for i, variable in enumerate(self.variables_list):
			if variable.centrosymmetry:
				number_of_centrosymmetric_terms += self.derivative_array[i]
	

		return ((number_of_centrosymmetric_terms % 2) == 1)


	def __str__(self):
		"""
		Returns a string like (1/2)*f[2,0,0,0,0,0]*u_1^2.
		"""

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





class TaylorExpansion(object):
	"""
	Represents a taylor expansion of an analytical function of variables.
	"""

	def __init__(self, term_acceptance_function):
		"""
		term_acceptance_function should be a function that takes in an expansion term instance and returns True if the term should be kept in the expansion, false otherwise.
		"""

		self.expansion_terms_list = []
		self.term_acceptance_function = term_acceptance_function

		self.populate_terms()


	def __str__(self):
		return ' + '.join(str(expansion_term) for expansion_term in self.expansion_terms_list)

	def __len__(self):
		return len(self.expansion_terms_list)

	def populate_terms(self):
		"""
		Create the terms in this expansion based on the given constraints.
		"""


		for i, variable in enumerate(variables):
			expansion_term = ExpansionTerm(variables)

			expansion_term.update_derivatives_list([i])

			if self.term_acceptance_function(expansion_term):
				self.expansion_terms_list.append(expansion_term)



		for i in range(len(variables)):
			for j in range(i, len(variables)):
				expansion_term = ExpansionTerm(variables)

				expansion_term.update_derivatives_list([i, j])

				self.expansion_terms_list.append(expansion_term)


		for i in range(len(variables)):
			for j in range(i, len(variables)):
				for k in range(j, len(variables)):
					expansion_term = ExpansionTerm(variables)

					expansion_term.update_derivatives_list([i, j, k])

					self.expansion_terms_list.append(expansion_term)


		for i in range(len(variables)):
			for j in range(i, len(variables)):
				for k in range(j, len(variables)):
					for l in range(k, len(variables)):
						expansion_term = ExpansionTerm(variables)

						expansion_term.update_derivatives_list([i, j, k, l]) ########only add if all the same displacement!

						self.expansion_terms_list.append(expansion_term)





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

	def remove_pure_displacement_terms(self):
		remove_list = []

		for i, expansion_term in enumerate(self.expansion_terms_list):
			if expansion_term.is_pure_type('displacement'):
				remove_list.append(expansion_term)

		for expansion_term in remove_list:
			self.expansion_terms_list.remove(expansion_term)








remove_pure_strain_terms = True
remove_pure_displacement_terms = False
remove_terms_by_symmetry = True
order = 2

strain_count = 3
displacement_count = 6


variables = []


for i in range(strain_count):
	variables.append(Variable('strain', i+2))

for i in range(displacement_count):
	variables.append(Variable('displacement', i, centrosymmetry=True))

print "Variables list: " + '[' + ", ".join(str(variable) for variable in variables) + ']'



def term_acceptance_function(expansion_term):

	if expansion_term.order == 1: #assumes no forces or stresses on the cell
		return False

	if expansion_term.is_centrosymmetric():
		return False

		ret 



	return True


taylor_expansion = TaylorExpansion(term_acceptance_function)

# if remove_terms_by_symmetry:
# 	taylor_expansion.remove_zero_terms_by_symmetry()

# if remove_pure_strain_terms:
# 	taylor_expansion.remove_pure_strain_terms()

# if remove_pure_displacement_terms:
# 	taylor_expansion.remove_pure_displacement_terms()

print
print "Number of terms:", len(taylor_expansion)


print '\n\t\t',
print taylor_expansion
print '\n'*3