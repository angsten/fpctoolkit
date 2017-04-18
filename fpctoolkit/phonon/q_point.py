#from fpctoolkit.phonon.q_point import QPoint

import numpy as np

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.structure.structure import Structure


class QPoint(object):
	"""
	Represents a single qpoint taken from the .
	"""

	def __init__(self, q_point_fractional_coordinates, normal_modes_list, primitive_cell_structure):
		"""
		The q_point input argument should be a tuple of three real numbers in reduced coordinates with no factor of 2Pi, e.g. (0.5, 0.5, 0.0).

		normal_modes_list should be a list of normal modes with identical q_point values. This list should be arranged by order of band_index.
		"""

		if not len(q_point_fractional_coordinates) == 3:
			raise Exception("Qpoint argument must have three compononents. Argument is", q_point_fractional_coordinates)

		Structure.validate(primitive_cell_structure)

		if not len(primitive_cell_structure)*3 == len(normal_modes_list):
			raise Exception("Number of normal mode instances should be equal to the number of atoms in the primitive cell times three. Normal_modes_list is", 
				normal_modes_list, "primitive structure is", primitive_cell_structure)


		self.q_point_fractional_coordinates = q_point_fractional_coordinates
		self.normal_modes_list = normal_modes_list
		self.primitive_cell_structure = primitive_cell_structure

		self.validate_normal_modes_list()

	def validate_normal_modes_list(self):

		for band_index, normal_mode in enumerate(normal_modes_list):
			if not normal_mode.q_point_fractional_coordinates == self.q_point_fractional_coordinates:
				raise Exception("Normal mode instance qpoints list", normal_mode.q_point_fractional_coordinates, "and QPoint instance qpoints", self.q_point_fractional_coordinates, "are not equivalent.")

			if not band_index == normal_mode.band_index:
				raise Exception("Normal modes list is not ordered by increasing band_index")



	def __str__(self):

		#print here
		return "under work"