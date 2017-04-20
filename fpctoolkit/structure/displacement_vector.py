#from fpctoolkit.structure.displacement_vector import DisplacementVector

import numpy as np
import copy

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.structure.structure import Structure


class DisplacementVector(object):
	"""
	Represents a displacement vector for a supercell. This vector has an x, y, and z 
	component of displacement for each atom in the cell (can be a supercel). It is thus of length 3*Nat*Ncell.
	"""

	def __init__(self, reference_structure, coordinate_mode='Cartesian'):
		"""
		"""

		Structure.validate(reference_structure)

		if not coordinate_mode in ['Cartesian', 'Direct']:
			raise Exception("Invalid coordinate mode given:", coordinate_mode)


		self.reference_structure = reference_structure

		self.displacement_vector = [0.0]*3.0*reference_structure.site_count

		self.coordinate_mode = coordinate_mode

	def __len__(self):
		return len(self.displacement_vector)

	def __getitem__(self, index):
		basic_validators.validate_sequence_index(index, len(self.displacement_vector))

		return self.displacement_vector[index]

	def __setitem__(self, index, value):
		basic_validators.validate_real_number(value)

		basic_validators.validate_sequence_index(index, len(self.displacement_vector))

		self.displacement_vector[index] = value



	def get_displaced_structure(self, input_reference_structure=None):
		"""
		Adds self.displacement_vector to the positions of the input reference structure to get a new structure. If reference_structure
		is None, the stored reference structure is used.
		"""

		reference_structure = input_reference_structure if input_reference_structure != None else self.reference_structure



		return DisplacementVector.displace_structure(reference_structure, self.displacement_vector, self.coordinate_mode)


	@staticmethod
	def displace_structure(self, reference_structure, displacement_vector, displacement_coordinate_mode):
		"""
		Adds displacement_vector to the positions of the input reference structure and returns a new structure. 
		"""

		if len(displacement_vector) != 3*reference_structure.site_count:
			raise Exception("Displacement vector size is not equal to the reference structures site count times three. Lengths are", 
				len(displacement_vector), 3*reference_structure.site_count)


		if not displacement_coordinate_mode in ['Cartesian', 'Direct']:
			raise Exception("Invalid coordinate mode given:", displacement_coordinate_mode)

		displaced_structure = copy.deepcopy(reference_structure)

		displaced_structure.convert_sites_to_coordinate_mode(displacement_coordinate_mode)


		for i, site in enumerate(reference_structure):
			for j in range(3):
				site['position'][j] += self.displacement_vector[j + i*3]