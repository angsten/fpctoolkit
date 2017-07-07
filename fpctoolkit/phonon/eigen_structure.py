#from fpctoolkit.phonon.eigen_structure import EigenStructure

import numpy as np
import copy
import random

from fpctoolkit.util.path import Path
import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.phonon.hessian import Hessian
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.displacement_vector import DisplacementVector
from fpctoolkit.phonon.eigen_component import EigenComponent

class EigenStructure(object):
	"""
	Represents a structure whose displacements are relative to a reference structure in terms of six strains (Voigt) and N displacement modes, where N is the number
	of atoms in the reference structure. The displacement modes are the eigen vectors of the hessian matrix for the reference structure.

	The representation is covered by two lists. One list is the engineering strains [eta_xx, eta_yy, eta_zz, eta_yz, eta_xz, eta_xy]. The other is the set of
	amplitudes representing degree of displacement along each normal mode. This set is stored as a list of EigenComponent instances, which store amplitudes and EigenPair
	instances.

	We can think of an eigenchromosome storing all of an eigenstructure's data looking like:

	[eta_xx, eta_yy, eta_zz, eta_yz, eta_xz, eta_xy, A_1, A_2, A_3, A_4, ..., A_N], where A_1 is the amplitude of the displacement eigen-vector with the lowest eigenvector and A_N
	is the amplitude of the displacement eigen-vector with the highest eigenvalue.

	If e_1, e_2, ..., e_N is the set of eigen-vectors, the total displacement is given by:

	U = A_1*e_1 + A_2*e_2 + ... + A_N*e_N



	When distorting a structure, displacements are always applied first (so they're in Lagrangian coordinates) and then strains are applied.
	When recovering the strains and eigen_component amplitudes from a structure, strains are removed first, then displacement amplitudes are determined.

	Note: if exx = 0.0, these means no strain in xx direction.
	"""

	def __init__(self, reference_structure, hessian, distorted_structure=None):
		"""
		If distorted_structure is inputted, then this will be used to seed the strain vector and eigen_component amplitudes.
		"""

		Structure.validate(reference_structure)

		eigen_pairs = hessian.get_sorted_hessian_eigen_pairs_list()

		# for eigen_pair in eigen_pairs:
		# 	print eigen_pair


		self.voigt_strains_list = [0.0]*6

		self.eigen_components_list = []

		for eigen_pair in eigen_pairs:
			eigen_component = EigenComponent(eigen_pair, amplitude=0.0)

			self.eigen_components_list.append(eigen_component)

		if len(self.eigen_components_list) != 3*reference_structure.site_count:
			raise Exception("Number of eigen components", len(self.eigen_components_list), "and number of degrees of freedom in reference structure", 3*reference_structure.site_count, "are not equal.")


		self.reference_structure = reference_structure


		if distorted_structure:
			self.set_strains_and_amplitudes_from_distorted_structure(distorted_structure)



	def set_eigen_chromosome(self, eigen_chromosome):
		"""
		eigen_chromosome is a list that looks like: [eta_xx, eta_yy, eta_zz, eta_yz, eta_xz, eta_xy, A_1, A_2, A_3, A_4, ..., A_N]
		This list does not have to extend all the way to A_N - if it does not, the remaining values are set to zero.
		"""

		for i in range(len(self)):
			if i < len(eigen_chromosome):
				self[i] = eigen_chromosome[i]
			else:
				self[i] = 0.0

		#self.set_translational_eigen_component_amplitudes_to_zero() #**do we want to do this always?**!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!set elsewhere too



	def set_translational_eigen_component_amplitudes_to_zero(self):
		for eigen_component in self.eigen_components_list:
			if eigen_component.is_translational_mode():
				eigen_component.amplitude = 0.0




	def get_distorted_structure(self):
		"""
		Apply the strains in voigt strains list and the displacements in the eigen_components list to the reference structure and return the new structure.
		"""

		total_displacement_vector = np.asarray([0.0]*3*self.reference_structure.site_count)

		for eigen_component in self.eigen_components_list:
			total_displacement_vector += eigen_component.get_displacement_vector()


		distorted_structure = DisplacementVector.displace_structure(reference_structure=self.reference_structure, displacement_vector=total_displacement_vector, displacement_coordinate_mode='Cartesian')

		distorted_structure.lattice.strain(self.get_strain_tensor())

		return distorted_structure

	def get_decomposed_structures(self, distorted_structure, threshold=0.1):
		"""
		Finds all active modes in distorted_structure and separates them out into the consituent mode distorted structures. The list of such structures is returned
		"""

		decomposed_structures_list = []

		self.set_strains_and_amplitudes_from_distorted_structure(distorted_structure)

		full_eigen_chromosome = self.get_list_representation()

		for i in range(6, len(full_eigen_chromosome)):

			if abs(full_eigen_chromosome[i]) > threshold:
				new_chromosome = [0.0]*len(full_eigen_chromosome)

				new_chromosome[:6] = full_eigen_chromosome[:6]

				new_chromosome[i] = full_eigen_chromosome[i]

				self.set_eigen_chromosome(new_chromosome)

				new_structure = self.get_distorted_structure()

				decomposed_structures_list.append(new_structure)

		return decomposed_structures_list






	def get_strain_tensor(self):
		"""
		Converts voigt strains stored in self.voigt_strains_list to a 3x3 tensor and returns this tensor.
		Upper triangle form is used.
		"""

		e = self.voigt_strains_list

		strain_tensor = [[1.0+e[0], e[5], e[4]], 
						 [0.0, 1.0+e[1], e[3]], 
						 [0.0, 0.0, 1.0+e[2]]]

		return strain_tensor




	def set_strains_and_amplitudes_from_distorted_structure(self, input_displaced_structure):
		"""
		Modifies the passed in voigt strains and eigen_components list such that the strains and amplitudes would reproduce the input displaced_structure if 
		get_displaced_structure were called.
		"""


		displaced_structure = copy.deepcopy(input_displaced_structure)

		strain_tensor = displaced_structure.lattice.get_strain_tensor_relative_to_reference(reference_lattice=self.reference_structure.lattice)


		exx = strain_tensor[0][0] - 1.0
		eyy = strain_tensor[1][1] - 1.0
		ezz = strain_tensor[2][2] - 1.0

		eyz = strain_tensor[1][2] + strain_tensor[2][1] #be careful of this double summation, but should work fine
		exz = strain_tensor[0][2] + strain_tensor[2][0]
		exy = strain_tensor[0][1] + strain_tensor[1][0]

		self.voigt_strains_list = [exx, eyy, ezz, eyz, exz, exy]


		displaced_structure.lattice = copy.deepcopy(self.reference_structure.lattice) #remove all strains before finding displacement amplitudes


		total_displacement_vector_instance = DisplacementVector.get_instance_from_displaced_structure_relative_to_reference_structure(reference_structure=self.reference_structure, 
			displaced_structure=displaced_structure, coordinate_mode='Cartesian')

		total_displacement_vector = total_displacement_vector_instance.to_numpy_array()

		for eigen_component in self.eigen_components_list:
			basis_vector = eigen_component.eigenvector

			projection = np.dot(basis_vector, total_displacement_vector)

			# print "projection: ", projection, "     Basis Vector: ", " ".join(str(x) for x in basis_vector)

			if abs(projection) < 1e-10:
				projection = 0.0

			eigen_component.amplitude = projection


		#self.set_translational_eigen_component_amplitudes_to_zero() #**do we want to do this always?**

	def get_mode_distorted_structures_list(self, amplitude=0.5):
		"""
		Takes the list of all displacement modes, applies them with significant amplitude to the reference structure, and returns the corresponding list of distorted structures.
		Useful for visualizing the displacement modes.
		"""

		structures_list = []

		for eigen_component in self.eigen_components_list:
			eigen_component.amplitude = amplitude

			structures_list.append(self.get_distorted_structure())

			eigen_component.amplitude = 0

		return structures_list




	def get_list_representation(self):
		"""
		Returns list of strains and distortion amplitudes like:
		[eta_xx, eta_yy, eta_zz, eta_yz, eta_xz, eta_xy, A_1, A_2, A_3, A_4, ..., A_N]
		"""

		return self.voigt_strains_list + [eigen_component.amplitude for eigen_component in self.eigen_components_list]


	def get_random_structure(self, mode_count_cutoff, max_amplitude):
		"""
		Returns a random structure with chromosome that looks like [0.0 0.0 rand 0.0 0.0 0.0    rand(-max_amplitude, max_amplitude) rand rand rand rand ... up to mode_count_cutoff of these]
		"""

		chromosome = [0.0, 0.0, random.uniform(-0.04, 0.04), 0.0, 0.0, 0.0] + [0.0]*mode_count_cutoff

		for i in range(mode_count_cutoff):
			if not self.eigen_components_list[i].is_translational_mode():
				chromosome[i+6] = random.uniform(-1.0*max_amplitude, 1.0*max_amplitude)


		print "Random chromosome is " + str(chromosome)

		self.set_eigen_chromosome(chromosome)

		return self.get_distorted_structure()


	def print_eigen_components(self):
		for i, eigen_component in enumerate(self.eigen_components_list):
			print "Index: " + str(i) + "   " + str(eigen_component)


	def __str__(self):
		voigt_strings = ['exx', 'eyy', 'ezz', 'eyz', 'exz', 'exy']
		return_string = "["

		rnd = 5

		return_string += ", ".join(voigt_strings[i] + '=' + str(round(strain,rnd)) for i, strain in enumerate(self.voigt_strains_list)) 

		for i, eigen_component in enumerate(self.eigen_components_list):
			return_string += ", " + 'A' + str(i) + '=' + str(round(eigen_component.amplitude, rnd))

			if eigen_component.is_translational_mode():
				return_string += '*'

		return_string += "]"

		return return_string

	def __len__(self):
		return len(self.get_list_representation())

	def __getitem__(self, index):
		list_representation = self.get_list_representation()

		basic_validators.validate_sequence_index(index, len(list_representation))

		return list_representation[index]

	def __setitem__(self, index, value):
		list_representation = self.get_list_representation()

		basic_validators.validate_real_number(value)

		basic_validators.validate_sequence_index(index, len(list_representation))

		if index <= 5:
			self.voigt_strains_list[index] = value
		else:
			self.eigen_components_list[index-6].amplitude = value