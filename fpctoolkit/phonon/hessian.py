#from fpctoolkit.phonon.hessian import Hessian

import numpy as np
import copy

import fpctoolkit.util.string_util as su
import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.phonon.hessian_eigen_pair import HessianEigenPair


class Hessian(object):
	"""
	Represents the second derivative matrix of the energy as a function of atomic displacements.
	"""

	def __init__(self, outcar):
		"""
		outcar should be an initialized Outcar instance from a force constants calculation.
		"""

		original_matrix = np.asarray(outcar.get_hessian_matrix())

		Hessian.validate_matrix_is_sufficiently_symmetric(original_matrix)


		self.hermitian_matrix = Hessian.get_hermitian_matrix(original_matrix)




	def get_sorted_hessian_eigen_pairs_list(self):
		"""
		Returns a list of HessianEigenPair instances.
		The eigen vectors are checked to make sure they form a proper orthonormal basis for displacements in the structure:
			Each vector must be orthogonal with each other
			Each vector must have a magnitude of one
			There must be exactly three translational modes
		"""

		eigenvalues, eigenvectors = np.linalg.eigh(self.hermitian_matrix)

		hessian_eigen_pairs_list = []

		for i in range(len(eigenvalues)):
			hessian_eigen_pairs_list.append(HessianEigenPair(eigenvalue=eigenvalues[i], eigenvector=eigenvectors[:, i]))


		Hessian.validate_translational_modes_in_eigen_pair_list(hessian_eigen_pairs_list)
		Hessian.validate_eigen_pairs_are_orthonormal(hessian_eigen_pairs_list)

		sorted_hessian_eigen_pairs_list = Hessian.get_sorted_eigen_pairs_list(hessian_eigen_pairs_list)


		self.translational_mode_indices = []

		for i, eigen_pair in enumerate(sorted_hessian_eigen_pairs_list):
			if eigen_pair.is_translational_mode():
				self.translational_mode_indices.append(i)

		return sorted_hessian_eigen_pairs_list


	def print_eigen_components(self):
		for i, eigen_pair in enumerate(self.get_sorted_hessian_eigen_pairs_list()):
			print "Index: " + str(i) + "\n" + str(eigen_pair)

	


	@staticmethod
	def validate_translational_modes_in_eigen_pair_list(eigen_pairs_list):
		translational_count = 0

		for eigen_pair in eigen_pairs_list:
			if eigen_pair.is_translational_mode():
				translational_count += 1

		if not translational_count == 3:
			raise Exception("Number of translational modes in eigen list must be exactly three.", translational_count)

	@staticmethod
	def validate_eigen_pairs_are_orthonormal(eigen_pairs_list):
		for i in range(0, len(eigen_pairs_list)):
			eigen_pairs_list[i].validate_eigenvector_is_normalized()

			for j in range(i+1, len(eigen_pairs_list)):
				eigen_pairs_list[i].validate_eigen_pair_is_orthogonal_to(eigen_pairs_list[j])

	@staticmethod
	def get_sorted_eigen_pairs_list(eigen_pairs_list):

		return sorted(eigen_pairs_list, key=lambda eigen_pair: eigen_pair.eigenvalue)



				

	def __str__(self):
		output_string = ""

		f = su.pad_decimal_number_to_fixed_character_length
		rnd = 4
		pad = 6

		for i in range(len(self.hermitian_matrix)):
			for j in range(len(self.hermitian_matrix)):
				output_string += f(self.hermitian_matrix[i][j], rnd, pad)
			output_string += '\n'

		return output_string


	@staticmethod
	def validate_matrix_is_sufficiently_symmetric(matrix):
		pass


		#implement

	@staticmethod
	def get_hermitian_matrix(matrix):
		"""
		Returns a modified matrix that is Hermitian (real and symmetric Transpose(A) = A).
		"""

		real_array = np.isreal(matrix)

		if len(filter(lambda x: not x, real_array.flatten())) != 0:
			raise Exception("Hessian matrix must be real to be hermitian.", matrix)


		return (matrix + matrix.T)/2.0



