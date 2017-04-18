#from fpctoolkit.phonon.q_point import QPoint

import numpy as np

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.structure.structure import Structure


class QPoint(object):
	"""
	Represents a single qpoint taken from the .
	"""

	def __init__(self, q_point_ primitive_cell_structure):
		"""
		normalized_eigen_displacements should be a list that looks like [atom_1_x_component_of_displacement_complex_number, atom_1_y..., ..., atom_2_x, ...] 
		and should be of length Nat, where Nat is the number of atoms in the primitive cell used to generate the phonon band structure.
		"""

		complex_vector_magnitude = np.linalg.norm(normalized_eigen_displacements)

		basic_validators.validate_approximately_equal(complex_vector_magnitude, 1.0, tolerance=0.000001)

		basic_validators.validate_real_number(frequency)

		Structure.validate(primitive_cell_structure)


		self.eigen_displacements_list = normalized_eigen_displacements
		self.frequency = frequency
		self.q_point = q_point
		self.band_index = band_index
		self.primitive_cell_structure = primitive_cell_structure
