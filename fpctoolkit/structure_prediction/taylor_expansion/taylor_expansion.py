#from fpctoolkit.structure_prediction.taylor_expansion.taylor_expansion import TaylorExpansion


from fpctoolkit.structure_prediction.taylor_expansion.expansion_term import ExpansionTerm


class TaylorExpansion(object):
	"""
	Represents a taylor expansion of an analytical function of variables.
	"""

	def __init__(self, variables_list, term_acceptance_function):
		"""
		variables_list is the list of all possible variables (as variable instances) in the taylor expansion.
		term_acceptance_function should be a function that takes in an expansion term instance and returns True if the term should be kept in the expansion, false otherwise.
		"""

		self.variables_list = variables_list
		self.term_acceptance_function = term_acceptance_function

		self.expansion_terms_list = []

		self.populate_terms()


	def __str__(self):
		return ' + '.join(str(expansion_term) for expansion_term in self.expansion_terms_list)

	def __len__(self):
		return len(self.expansion_terms_list)

	def populate_terms(self):
		"""
		Create the terms in this expansion based on the given constraints.
		"""

		full_expansion_terms_list = []

		for i, variable in enumerate(self.variables_list):
			expansion_term = ExpansionTerm(self.variables_list)

			expansion_term.update_derivatives_list([i])


			full_expansion_terms_list.append(expansion_term)



		for i in range(len(self.variables_list)):
			for j in range(i, len(self.variables_list)):
				expansion_term = ExpansionTerm(self.variables_list)

				expansion_term.update_derivatives_list([i, j])

				full_expansion_terms_list.append(expansion_term)


		for i in range(len(self.variables_list)):
			for j in range(i, len(self.variables_list)):
				for k in range(j, len(self.variables_list)):
					expansion_term = ExpansionTerm(self.variables_list)

					expansion_term.update_derivatives_list([i, j, k])

					full_expansion_terms_list.append(expansion_term)


		for i in range(len(self.variables_list)):
			for j in range(i, len(self.variables_list)):
				for k in range(j, len(self.variables_list)):
					for l in range(k, len(self.variables_list)):
						expansion_term = ExpansionTerm(self.variables_list)

						expansion_term.update_derivatives_list([i, j, k, l]) ########only add if all the same displacement!

						full_expansion_terms_list.append(expansion_term)



		for expansion_term in full_expansion_terms_list:
			if self.term_acceptance_function(expansion_term):
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

