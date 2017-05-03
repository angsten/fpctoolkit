#from fpctoolkit.phonon.eigen_structure import EigenStructure

import numpy as np
import copy

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

	We can think of a eigenchromosome storing all of an eigenstructure's data looking like:

	[eta_xx, eta_yy, eta_zz, eta_yz, eta_xz, eta_xy, A_1, A_2, A_3, A_4, ..., A_N], where A_1 is the amplitude of the displacement eigen-vector with the lowest eigenvector and A_N
	is the amplitude of the displacement eigen-vector with the highest eigenvalue.

	If e_1, e_2, ..., e_N is the set of eigen-vectors, the total displacement is given by:

	U = A_1*e_1 + A_2*e_2 + ... + A_N*e_N



	When distorting a structure, displacements are always applied first (so they're in Lagrangian coordinates) and then strains are applied.
	When recovering the strains and eigen_component amplitudes from a structure, strains are removed first, then displacement amplitudes are determined.
	"""

	def __init__(self, reference_structure, hessian, distorted_structure=None):
		"""
		If distorted_structure is inputted, then this will be used to seed the strain vector and eigen_component amplitudes.
		"""

		Structure.validate(reference_structure)

		eigen_pairs = hessian.get_sorted_hessian_eigen_pairs_list()


		self.voigt_strains_list = [0.0]*6

		self.eigen_components_list = []

		for eigen_pair in eigen_pairs:
			eigen_component = EigenComponent(eigen_pair, amplitude=0.0)

			self.eigen_components_list.append(eigen_component)

		if len(self.eigen_components_list) != 3*reference_structure.site_count:
			raise Exception("Number of eigen components", len(self.eigen_components_list), "and number of degrees of freedom in reference structure", 3*reference_structure.site_count, "are not equal.")


		self.reference_structure = reference_structure


		if distorted_structure:
			pass



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


		displaced_structure = DisplacementVector.displace_structure(reference_structure=self.reference_structure, displacement_vector=total_displacement_vector, displacement_coordinate_mode='Cartesian')



		#####apply strains here############



		return displaced_structure


	def get_list_representation(self):
		"""
		Returns list of strains and distortion amplitudes like:
		[eta_xx, eta_yy, eta_zz, eta_yz, eta_xz, eta_xy, A_1, A_2, A_3, A_4, ..., A_N]
		"""

		return self.voigt_strains_list + [eigen_component.amplitude for eigen_component in self.eigen_components_list]



	def __str__(self):
		return_string = "["

		return_string += ", ".join(str(strain) for strain in self.voigt_strains_list)

		for eigen_component in self.eigen_components_list:
			return_string += ", " + str(eigen_component.amplitude)

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