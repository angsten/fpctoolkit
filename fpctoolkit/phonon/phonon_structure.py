#from fpctoolkit.phonon.phonon_structure import PhononStructure

import numpy as np
import copy
from collections import OrderedDict
import math
import cmath
import sys

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.structure_manipulator import StructureManipulator
from fpctoolkit.phonon.normal_coordinate import NormalCoordinate
from fpctoolkit.util.math.vector import Vector
from fpctoolkit.structure.displacement_vector import DisplacementVector
from fpctoolkit.phonon.phonon_super_displacement_vector import PhononSuperDisplacementVector

class PhononStructure(object):
	"""
	Represents a structure whose distortions are characterized by a set of 'complex normal coordinates', Q_q,j (see around page 298 of Born and Huang and pages preceding).
	"""

	def __init__(self, primitive_cell_structure, phonon_band_structure, supercell_dimensions_list, normal_coordinate_instances_list=None):
		"""
		primitive_cell_structure should be the primitive cell Structure class instance that was used to generate the phonon band structure.

		phonon_band_structure should be a PhononBandStructure instance with, at minimim, normal modes for the necessary wave vectors, loosely (38.10, pg 295 Born and Huang)
		-->For example, if a 2x1x1 supercell is expected, the following q points must be provided: (+1/2, 0, 0), (0, 0, 0)

		supercell_dimensions

		if normal_coordinate_instances_list, this list is used to set the normal coordinates, else, the normal coordinates are initialized to zero.
		"""

		Structure.validate(primitive_cell_structure)

		self.primitive_cell_structure = primitive_cell_structure
		self.phonon_band_structure = phonon_band_structure
		self.supercell_dimensions_list = supercell_dimensions_list

		#the total number of degrees of freedom to describe the ionic displacments of the system
		self.dof_count = 3*self.primitive_cell_structure.site_count*self.supercell_dimensions_list[0]*self.supercell_dimensions_list[1]*self.supercell_dimensions_list[2]

		self.reference_supercell_structure = StructureManipulator.get_supercell(primitive_cell_structure, supercell_dimensions_list)



		self.validate_necessary_wave_vectors_exist()


		#FIX::self.number_of_normal_coordinates = 2*self.primitive_cell_structure.site_count*3*supercell_dimensions_list[0]*supercell_dimensions_list[1]*supercell_dimensions_list[2]


		if normal_coordinate_instances_list != None:
			# if len(normal_coordinate_instances_list) != self.number_of_normal_coordinates:
			# 	raise Exception("The number of given normal coordinates is not equal to the number needed to describe the structural distortions. Normal coordinates list given is", normal_coordinate_instances_list)
			# else:
			self.normal_coordinates_list = copy.deepcopy(normal_coordinate_instances_list)
		else:
			self.initialize_normal_coordinates_list()

	def __str__(self):
		return "[\n" + "\n".join(str(normal_coordinate) for normal_coordinate in self.normal_coordinates_list) + "\n]"


	def initialize_displacement_basis_vectors(self):
		"""
		Determine the set of phonon super displacement vectors that form a normal basis without any redundant vectors (vectors sharing the hyperplane with other vectors).
		The basis vectors are stored in self.basis_phonon_displacement_vector_list, a list of PhononSuperDisplacementVector instances.

		There should always be Ncell*Nat*3 vectors in this basis - one for each vector in the ionic displacement basis for the supercell
		"""

		self.basis_phonon_displacement_vector_list = []
		superfluous_basis = []

		for normal_mode in self.phonon_band_structure.get_list_of_normal_modes():
			for lambda_index in [1, 2]:
				normal_mode_displacement_vector = PhononSuperDisplacementVector(normal_mode_instance=normal_mode, lambda_index=lambda_index, 
					reference_supercell=self.reference_supercell_structure, supercell_dimensions_list=self.supercell_dimensions_list)

				if normal_mode_displacement_vector.magnitude > PhononSuperDisplacementVector.zero_vector_magnitude_tolerance:
					superfluous_basis.append(normal_mode_displacement_vector)

		#self.basis_phonon_displacement_vector_list now has only the non-zero vectors. However, many of these may be redundant - i.e. we don't need all of them to span the 
		#space of ionic displacements in the supercell.


		#we should build up the basis from lowest frequency components to highest, because this will lead to a basis that most easily descends the energy landscape.
		#By sorting the superfluous basis by normal mode frequency squared first, we increase the chances of the basis being composed of low energy phonon modes.
		#This is because the algorithm below kicks out basis vectors later in the superfluous_basis list that can be described by those that come before.

		sorted_superfluous_basis = sorted(superfluous_basis, key=lambda x: x.normal_mode.eigenvalue)


		for i in range(0, len(sorted_superfluous_basis)):

			if len(sorted_superfluous_basis[i]) != self.dof_count:
				raise Exception("Basis vector does not have the correct number of degrees of freedom", len(sorted_superfluous_basis[i]), " should be", self.dof_count)

			total_displacement_vector_set = self.basis_phonon_displacement_vector_list + [sorted_superfluous_basis[i]]

			if DisplacementVector.no_vector_in_set_is_in_span_of_others(total_displacement_vector_set):
				self.basis_phonon_displacement_vector_list.append(sorted_superfluous_basis[i])

		#print "Length of basis is:", len(self.basis_phonon_displacement_vector_list)
		
		if len(self.basis_phonon_displacement_vector_list) != self.dof_count:
			raise Exception("After pruning the basis set, the number of basis displacement vectors", len(self.basis_phonon_displacement_vector_list), 
				"does not equal the number of degrees of freedom needed to describe supercell displacements", self.dof_count)


	def initialize_normal_coordinates_list(self):
		"""
		Create the list of normal coordinates (all initially zero) that describe the displacements by acting as coefficients on the phonon displacement vector basis.
		"""

		self.initialize_displacement_basis_vectors()

		self.normal_coordinates_list = []

		for basis_phonon_displacment_vector in self.basis_phonon_displacement_vector_list:
			normal_coordinate = NormalCoordinate(normal_mode_instance=basis_phonon_displacment_vector.normal_mode, lambda_index=basis_phonon_displacment_vector.lambda_index, 
				coefficient=0.0, phonon_super_displacement_vector_instance=basis_phonon_displacment_vector)

			self.normal_coordinates_list.append(normal_coordinate)


	def validate_necessary_wave_vectors_exist(self):
		"""
		Validates that (at minimum) all necessary wavevectors for the given supercell_dimensions are in phonon_band_structure.
		"""

		necessary_q_vectors_list = self.get_necessary_wave_vectors_listt()

		for q_vector in necessary_q_vectors_list:
			if q_vector not in self.phonon_band_structure:
				raise Exception("Phonon band structure does not contain all necessary q_vectors. Missing ", q_vector)





	def get_necessary_wave_vectors_listt(self):
		"""
		Using equation 38.10 from B+H, determine all necessary wave vectors for the given supercell dimensions (resulting q's are in
		fractional coordinates)
		"""

		return PhononStructure.get_necessary_wave_vectors_list(self.supercell_dimensions_list)



	def get_distorted_supercell_structure(self):
		"""
		Returns a supercell of self.primitive_cell_structure with dimensions self.supercell_dimensions_list with the phonon eigen_displacements applied, as
		controlled by self.normal_coordinates_list
		"""

		distorted_structure = copy.deepcopy(self.reference_supercell_structure)

		total_supercell_displacment_vector = DisplacementVector(reference_structure=self.reference_supercell_structure, coordinate_mode='Cartesian')

		for normal_coordinate in self.normal_coordinates_list:
			total_supercell_displacment_vector += normal_coordinate.get_displacement_vector()


		return total_supercell_displacment_vector.get_displaced_structure(self.reference_supercell_structure)



	def set_translational_coordinates_to_zero(self):
		"""
		Sets all components of self.Q_coordinates_list that correspond to a translational normal mode that doesn't affect the structure's energy.
		"""

		pass

	@staticmethod
	def get_normal_coordinates_list_from_supercell_structure(self, supercell_structure):
		"""
		Returns a list of complex normal coordinates (Q) based on the current phonon band structure and the displacements in supercell_structure.
		Supercell_structure must be consistent in dimensions with self.supercell_dimensions.
		"""

		pass


	@staticmethod
	def get_necessary_wave_vectors_list(supercell_dimensions_list):
		"""
		Using equation 38.10 from B+H, determine all necessary wave vectors for the given supercell dimensions (resulting q's are in
		fractional coordinates). In this version, don't every use -q and q - just positive q's are sufficient.

		For example, for a 2x1x1 supercell, returned q points will be [(0.5, 0, 0), (0, 0, 0)]
		"""

		necessary_q_vectors_list = []
		L_x = supercell_dimensions_list[0]
		L_y = supercell_dimensions_list[1]
		L_z = supercell_dimensions_list[2]

		for l_x in range(0, L_x):
			for l_y in range(0, L_y):
				for l_z in range(0, L_z):
					q_point_x = float(l_x)/float(L_x)
					q_point_y = float(l_y)/float(L_y)
					q_point_z = float(l_z)/float(L_z)

					q_point = (q_point_x, q_point_y, q_point_z)

					q_point_necessary = True

					for q_component in q_point:
						if (q_component > (0.5)):
							q_point_necessary = False

					if q_point_necessary:
						necessary_q_vectors_list.append(q_point)

		# if len(necessary_q_vectors_list) != L_x*L_y*L_z:
		# 	raise Exception("Number of necessary wave-vectors must equal the number of cells in the supercell.")

		return necessary_q_vectors_list