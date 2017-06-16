#from fpctoolkit.phonon.hessian import Hessian

import numpy as np
import copy

import fpctoolkit.util.string_util as su
import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.phonon.hessian_eigen_pair import HessianEigenPair
from fpctoolkit.io.file import File


class Hessian(object):
	"""
	Represents the second derivative matrix of the energy as a function of atomic displacements.
	"""

	def __init__(self, outcar):
		"""
		outcar should be an initialized Outcar instance from a force constants calculation.
		"""
		self.outcar = outcar

		original_matrix = np.asarray(self.outcar.get_hessian_matrix())

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


	def get_mode_effective_charge_vector(self, displacement_mode_vector, reference_structure):
		"""
		Returns the born effective charge dotted with the mode eigenvector associated with displacement_mode_vector. This resulting vector describes how the macroscopic polarization changes
		as the given displacement mode sets in.
		
	
		displacement_mode_vector should be a vector that is N*3 in length and looks like [disp_atom_1_x, disp_atom_1_y, ..., disp_atom_N_z]

		"""

		polarization_vector = [0.0, 0.0, 0.0]

		bec_tensor = self.outcar.get_born_effective_charge_tensor() #NEED TO DIVIDE BY VOLUME IN ANGSTROMS^3 first then mult by Angstroms with displacements, then convert to C/m^2 from e/A^2

		for atom_index in range(len(bec_tensor)):
			ion_3x3_tensor = bec_tensor[atom_index]

			for cartesian_direction_index in range(3):
				for polarization_direction_index in range(3):
					polarization_vector[polarization_direction_index] += displacement_mode_vector[cartesian_direction_index+atom_index*3]*ion_3x3_tensor[polarization_direction_index][cartesian_direction_index]


		cell_volume = reference_structure.get_volume()
		e = 1.6021766209*10**-19 #in coulombs
		angstroms_sq_per_meter_sq = 10**20
		conversion_factor = e*(1/cell_volume)*angstroms_sq_per_meter_sq

		###watch units!
		return [conversion_factor*component for component in polarization_vector]

	def print_mode_effective_charge_vectors_to_file(self, file_path, reference_structure):
		file = File()

		f = su.pad_decimal_number_to_fixed_character_length
		rnd = 4
		pad = 7

		for i, eigen_pair in enumerate(self.get_sorted_hessian_eigen_pairs_list()):
			index_string = str(i+1)

			while len(index_string) < 3:
				index_string += ' '

			file += "u_" + index_string + '   ' + f(eigen_pair.eigenvalue, 2, pad) + '      ' + " ".join(f(x, rnd, pad) for x in self.get_mode_effective_charge_vector(eigen_pair.eigenvector, reference_structure))
			#file += ''

		file.write_to_path(file_path)

	def print_eigen_components(self):
		for i, eigen_pair in enumerate(self.get_sorted_hessian_eigen_pairs_list()):
			print "Index: " + str(i) + "\n" + str(eigen_pair)

	def print_eigen_components_to_file(self, file_path):
		file = File()

		for i, eigen_pair in enumerate(self.get_sorted_hessian_eigen_pairs_list()):
			file += "Index: " + str(i) + "\n" + str(eigen_pair)
			file += ''

		file.write_to_path(file_path)

	def print_eigenvalues(self):
		for i, eigen_pair in enumerate(self.get_sorted_hessian_eigen_pairs_list()):
			print "u_" + str(i+1) + ": " + str(eigen_pair.eigenvalue)

	def print_eigenvalues_to_file(self, file_path):
		file = File()

		for i, eigen_pair in enumerate(self.get_sorted_hessian_eigen_pairs_list()):
			file += "u_" + str(i+1) + ": " + str(eigen_pair.eigenvalue)

		file.write_to_path(file_path)

	@staticmethod
	def validate_translational_modes_in_eigen_pair_list(eigen_pairs_list):
		translational_count = 0

		for eigen_pair in eigen_pairs_list:
			if eigen_pair.is_translational_mode():
				translational_count += 1

		return None #############################################################################################################################
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



