#from fpctoolkit.structure_prediction.taylor_expansion.expansion_term import ExpansionTerm

import numpy as np

from fpctoolkit.structure_prediction.taylor_expansion.variable import Variable



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

		self.derivative_coefficient = None

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
				self.coefficient = 1.0/2.0
				self.coefficient_string = '1/2'
			else:
				raise Exception("bad count", non_zero_count, self.derivative_array)
		elif order == 3:
			if non_zero_count == 1:
				self.coefficient = 1.0/6.0
				self.coefficient_string = '1/6'
			elif non_zero_count == 2:
				self.coefficient = 1.0/2.0
				self.coefficient_string = '1/2'
			elif non_zero_count == 3:
				self.coefficient = 1.0
				self.coefficient_string = ''
			else:
				raise Exception("bad count", non_zero_count, self.derivative_array)
		elif order == 4:
			if non_zero_count == 1:
				self.coefficient = 1.0/24.0
				self.coefficient_string = '1/24'
			elif non_zero_count == 2:
				if self.get_derivative_type() in ['31', '13']:
					self.coefficient = 1.0/6.0
					self.coefficient_string = '1/6'
				elif self.get_derivative_type() == '22':
					self.coefficient = 1.0/4.0
					self.coefficient_string = '1/12'
			elif non_zero_count == 3:
				if self.get_derivative_type() in ['211', '121', '112']:
					self.coefficient = 1.0/2.0
					self.coefficient_string = '1/2'
			elif non_zero_count == 4:
				if self.get_derivative_type() == '1111':
					self.coefficient = 1.0
					self.coefficient_string = ''
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

	def get_displacement_indices_list(self):
		indices_list = []

		for i, variable in enumerate(self.variables_list):
			if self.derivative_array[i] != 0 and variable.type_string == 'displacement':
				indices_list.append(variable.index)

		return indices_list

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

	def has_single_variable(self):
		"""
		Returns true if term has only one variable in it (regardless of order).
		"""

		if self.get_non_zero_count() == 1:
			return True
		else:
			return False

	def get_active_variables(self):
		"""
		Returns a list of variables that are included in this term.
		"""

		return [variable for i, variable in enumerate(self.variables_list) if self.derivative_array[i] > 0]

	def get_perturbation_np_derivative_array(self, perturbation_magnitudes_dictionary):
		"""
		perturbation_magnitudes_dictionary should look like {'strain': 0.02, 'displacement': 0.01} with strain as fractional and displacement in angstroms

		returns self.derivative_array but with the appropriate magnitudes swapped in for the non-zero components. Also, a second order component is still replaced with the same magnitude as a first order.
		"""

		np_derivative_array = np.array(self.get_unity_derivative_array())

		for i, variable in enumerate(self.variables_list):
			np_derivative_array[i] *= perturbation_magnitudes_dictionary[variable.type_string]

		return np_derivative_array

	def lower_first_displacement_order(self):
		"""
		Take first displacement variable with non-zero derivative and low the derivative array for this component by one:

		f[0, 2, 3, 4, 0, 2, 0, 0, 3, 0, 1] => f[0, 2, 3, 4, 0, 2, 0, 0, 3, 0, 1]
		"""

		if self.is_pure_type('strain'):
			raise Exception("Cannot find any displacement variables")

		for i, variable in enumerate(self.variables_list):
			if variable.type_string == 'displacement' and self.derivative_array[i] > 0:
				self.derivative_array[i] -= 1

				return

	def get_first_displacement_index(self):
		"""
		Finds first non-zero displacement derivative in derivative array and returns this variable's index
		"""

		if self.is_pure_type('strain'):
			raise Exception("Cannot find any displacement variables")

		for i, variable in enumerate(self.variables_list):
			if variable.type_string == 'displacement' and self.derivative_array[i] > 0:
				return variable.index



	def get_unity_derivative_array(self):
		"""
		f[1, 3, 0, 0, 4] => [1, 1, 0, 0, 1]
		"""

		unity_array = []
		for component in self.derivative_array:
			if component != 0.0:
				unity_array.append(1.0)
			else:
				unity_array.append(0.0)

		return unity_array

	def get_derivative_type(self):
		"""
		If f[1, 0, 0, ...], type is '1'
		If f[2, 0, 0, ...], type is '2'
		f[1, 1, 0, ...] is '11'
		f[2, 1, ...] is '21'
		f[1, 2, ...] is '12'
		f[4, 0, 0, ...] is '4'
		"""

		return "".join(str(component) for component in self.get_list_of_non_zero_elements_in_derivative_array())

	def get_list_of_non_zero_elements_in_derivative_array(self):
		"""
		f[1, 0, 0, 4, 0, 2] would return [1, 4, 2]
		"""

		non_zero_elements_list = []

		for component in self.derivative_array:
			if component != 0:
				non_zero_elements_list.append(component)

		return non_zero_elements_list


	def get_variable_portion_string(self):
		output_string = ''

		for index, derivative_value in enumerate(self.derivative_array):
			if derivative_value == 1:
				output_string += str(self.variables_list[index])
			elif derivative_value == 2:
				output_string += str(self.variables_list[index]) + "^2"
			elif derivative_value == 3:
				output_string += str(self.variables_list[index]) + "^3"
			elif derivative_value == 4:
				output_string += str(self.variables_list[index]) + "^4"
		
		return output_string

	def __str__(self):
		"""
		Returns a string like (1/2)*f[2,0,0,0,0,0]*u_1^2.
		"""

		output_string = ""

		if self.derivative_coefficient == None:
			if self.coefficient != 1.0:
				coefficient_string = '(' + self.coefficient_string + ')' + '*'
			else:
				coefficient_string = ''

			output_string += coefficient_string + 'f[' + ','.join(str(derivative_value) for derivative_value in self.derivative_array) + ']'
		else:
			output_string += str(self.derivative_coefficient*self.coefficient)

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
