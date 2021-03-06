#from fpctoolkit.phonon.phonon_band_structure import PhononBandStructure

import numpy as np
from collections import OrderedDict

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.structure.structure import Structure


class PhononBandStructure(object):
	"""
	Represents the entire set of qpoints and their associated frequencies and normal mode eigenvectors generated from a phonon calculation.

	Effectively, this class is an ordered dictionary of QPoint instances. These are stored in qpoints, and to get, for instance, the (0.5, 0.5, 0.0)
	QPoint instance, one should use phon_band_struct[(0.5, 0.5, 0.0)]
	"""

	def __init__(self, q_points_list, primitive_cell_structure):
		"""
		q_points_list should be the set of q_points instances. No particular ordering is necessary, but the order of this list will be preserved in the
		ordered dicitonary which stores this list.

		primitive_cell_structure should be the unit_cell used to generate the phonon normal mode data.
		"""

		Structure.validate(primitive_cell_structure)

		self.primitive_cell_structure = primitive_cell_structure

		
		self.initialize_q_points(q_points_list)

		self.validate_data()




	def initialize_q_points(self, q_points_list):
		self.q_points = OrderedDict()

		for q_point_instance in q_points_list:
			self.q_points[q_point_instance.q_point_fractional_coordinates] = q_point_instance


	def validate_data(self):
		"""
		Validate that the eigenvalues and eigenvectors are valid based on properties of phonons.
		"""

		#check that eig_vec(q) = eig_vec*(-q) <- complex conjugate for all possible q other than (0 0 0)
		#check that three translational modes exist and that their frequencies are sufficiently close to zero
		#check that zone-centered eigenvectors are entirely real with no imaginary components
		#check that the direct orthonormal relations are satisfied within a tolerance (left realtion of 38.25 in Born and Huang, page 298)


		# translational_vectors_in_basis_list = filter(lambda x: x.normal_mode.translational, self.basis_phonon_displacement_vector_list)

		# if len(translational_vectors_in_basis_list) != 3:
		# 	raise Exception("Number of translational vectors is not equal to three. This may be a sign of an incomplete basis. Count is", len(translational_vectors_in_basis_list))

	def get_list_of_normal_modes(self):
		"""
		Returns list of normal mode instances ordered by both the order of QPoint additions to this class, and within that, the order in which the normal modes appear within the qpoint normal modes list.
		"""

		return [normal_mode for q_vector, q_point_instance in self.q_points.items() for normal_mode in q_point_instance.normal_modes_list]


	def __getitem__(self, key):
		if not isinstance(key, tuple) or len(key) != 3:
			raise Exception("Phonon band structure key must be a tuple of three real numbers. Key used is", key)

		return self.q_points[key]

	def __contains__(self, key):
		return key in self.q_points

	def __iter__(self):
		return iter(self.q_points)

	def __str__(self):

		join_string = "\n"*3 + 140*"*" + "\n"*4
		return join_string.join(str(value) for qpoint, value in self.q_points.items())