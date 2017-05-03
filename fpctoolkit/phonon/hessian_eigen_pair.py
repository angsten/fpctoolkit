#from fpctoolkit.phonon.hessian_eigen_pair import HessianEigenPair

import numpy as np
import copy

import fpctoolkit.util.string_util as su
import fpctoolkit.util.basic_validators as basic_validators


class HessianEigenPair(object):
	"""
	Represents a pair of eigen value and vector from a Hessian Martix.
	"""

	def __init__(self, eigenvalue, eigenvector):
		"""
		eigenvalue - float
		eigenvector - list of floats
		"""

		basic_validators.validate_real_number(eigenvalue)

		if len(eigenvector) < 3:
			raise Exception("Eigenvector list of values must have at least three components:", eigenvector)

		basic_validators.validate_sequence_of_real_numbers(eigenvector)


		self.eigenvalue = eigenvalue
		self.eigenvector = np.asarray(eigenvector)


	def is_unstable(self):
		return (self.eigenvalue < 0.0) and (not self.is_translational_mode())


	def is_translational_mode(self):
		x = self.eigenvector[0]
		y = self.eigenvector[1]
		z = self.eigenvector[2]

		reference_list = [x, y, z]

		tolerance = 0.01 #in Angstroms

		for i in range(1, len(self.eigenvector)/3):
			for j in range(3):
				if abs(self.eigenvector[i*3+j]-reference_list[j]) > tolerance:
					return False

		if abs(self.eigenvalue) > 0.05:
			raise Exception("What has been determined as a translational mode has an eigenvalue far from zero:", str(self))

		return True


	def validate_eigen_pair_is_orthogonal_to(self, eigen_pair_instance):
		"""
		Validates that this eigenpair instance's eigenvector is orthogonal to the input eigen_pair_instance's eigenvector.
		"""

		dot_product = np.dot(self.eigenvector, eigen_pair_instance.eigenvector)

		basic_validators.validate_approximately_equal(dot_product, 0.0, 1e-8)

	def validate_eigenvector_is_normalized(self):
		return basic_validators.validate_approximately_equal(self.magnitude, 1.0, 1e-8)


	@property
	def magnitude(self):
		return np.linalg.norm(self.eigenvector)


	def __str__(self):
		return_string = ""
		return_string += '-'*80 + "\n"

		if self.is_translational_mode():
			translational_string = "   *translational mode*\n\n"
		else:
			translational_string = "\n\n"

		return_string += "Eigenvalue: " + str(self.eigenvalue) + translational_string

		f = su.pad_decimal_number_to_fixed_character_length
		rnd = 5
		pad = 8
		for i in range(len(self.eigenvector)/3):
			return_string += "Atom " + str(i) + " " + f(self.eigenvector[3*i+0], rnd, pad) + " " + f(self.eigenvector[3*i+1], rnd, pad) + " " + f(self.eigenvector[3*i+2], rnd, pad) + "\n"

		return return_string