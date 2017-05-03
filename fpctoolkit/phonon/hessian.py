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








	def get_list_of_hessian_eigen_pairs(self):
		"""
		Returns a list of HessianEigenPair instances.
		The eigen vectors are checked to make sure they form a proper orthonormal basis for displacements in the structure:
			Each vector must be orthogonal with each other
			Each vector must have a magnitude of one
			There must be exactly three translational modes
		"""

		eigenvalues, eigenvectors = np.linalg.eigh(np_hess_refined)

		hessian_eigen_pair_list = []
		translational_count = 0

		for i in range(len(eigenvalues)):
			eigenvalue = eigenvalues[i]
			eigenvector = eigenvectors[:, i]

			hessian_eigen_pair = HessianEigenPair(eigenvalue, eigenvector)

			if hessian_eigen_pair.is_translational_mode():
				translational_count += 1

			hessian_eigen_pair_list.append(hessian_eigen_pair)

		if not translational_count == 3:
			raise Exception("Number of translational modes in eigen list must be exactly three.", translational_count)

		return hessian_eigen_pair_list



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



