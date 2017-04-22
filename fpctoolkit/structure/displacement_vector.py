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

		self.displacement_vector = [0.0]*3*reference_structure.site_count

		self.coordinate_mode = coordinate_mode

	def __str__(self):
		return "[" + ", ".join(str(component) for component in self.displacement_vector) + "]"

	def __len__(self):
		return len(self.displacement_vector)

	def __getitem__(self, index):
		basic_validators.validate_sequence_index(index, len(self.displacement_vector))

		return self.displacement_vector[index]

	def __setitem__(self, index, value):
		basic_validators.validate_real_number(value)

		basic_validators.validate_sequence_index(index, len(self.displacement_vector))

		self.displacement_vector[index] = value


	def __iadd__(self, displacement_vector):
		if len(displacement_vector) != len(self.displacement_vector):
			raise Exception("To add two displacement vectors, their lengths must be equal.", displacement_vector, self.displacement_vector)

		added_displacement_vector = copy.deepcopy(displacement_vector)

		for i in range(len(added_displacement_vector)):
			added_displacement_vector[i] += self.displacement_vector[i]

		return added_displacement_vector

	def __radd__(self, displacement_vector):
		if len(displacement_vector) != len(self.displacement_vector):
			raise Exception("To add two displacement vectors, their lengths must be equal.", displacement_vector, self.displacement_vector)

		added_displacement_vector = copy.deepcopy(displacement_vector)

		for i in range(len(added_displacement_vector)):
			added_displacement_vector[i] += self.displacement_vector[i]

		return added_displacement_vector

	def __imul__(self, scalar):
		if isinstance(scalar, complex):
			basic_validators.validate_complex_number(scalar)
		else:
			basic_validators.validate_real_number(scalar)

		multiplied_displacement_vector = copy.deepcopy(self)


		for i in range(len(multiplied_displacement_vector)):
			multiplied_displacement_vector[i] *= scalar

		return multiplied_displacement_vector

	__rmul__ = __imul__


	def is_zero_vector(self, zero_tolerance=1e-12):
		"""
		Returns true is the stored displacement vector magnitude is zero - then all components must be zero.
		"""

		return (self.magnitude < zero_tolerance)


	def set_magnitude(self, new_magnitude):
		"""
		Modifies the L2 norm of this vector to be equal to new_magnitude by increase or decreasing the component magnitudes.
		"""

		if new_magnitude == 0.0:
			factor = 0.0
		else:

			if self.is_zero_vector():
				raise Exception("Cannot alter the magnitude of a zero vector")

			factor = (new_magnitude/self.magnitude)


		for i in range(len(self.displacement_vector)):
			self.displacement_vector[i] *= factor

		basic_validators.validate_approximately_equal(self.magnitude, new_magnitude, tolerance=1e-8)

	def normalize(self):
		"""
		Alters the stored displacements such that the displacement vector magnitude is one.
		"""

		self.set_magnitude(1.0)


	def to_list(self):
		"""
		Returns the stored displacement vector as a list of values [0.2, 0.5, ...].
		"""

		return self.displacement_vector

	@property
	def magnitude(self):
		"""
		Returns L2 norm of the stored displacement vector.
		"""

		return np.linalg.norm(self.displacement_vector)

	def get_displaced_structure(self, input_reference_structure=None):
		"""
		Adds self.displacement_vector to the positions of the input reference structure to get a new structure. If reference_structure
		is None, the stored reference structure is used.
		"""

		reference_structure = input_reference_structure if input_reference_structure != None else self.reference_structure



		return DisplacementVector.displace_structure(reference_structure, self.displacement_vector, self.coordinate_mode)


	@staticmethod
	def displace_structure(reference_structure, displacement_vector, displacement_coordinate_mode):
		"""
		Adds displacement_vector to the positions of the input reference structure and returns a new structure. 
		"""

		if len(displacement_vector) != 3*reference_structure.site_count:
			raise Exception("Displacement vector size is not equal to the reference structures site count times three. Lengths are", 
				len(displacement_vector), 3*reference_structure.site_count)


		if not displacement_coordinate_mode in ['Cartesian', 'Direct']:
			raise Exception("Invalid coordinate mode given:", displacement_coordinate_mode)


		displaced_structure = copy.deepcopy(reference_structure)

		original_reference_coordinate_mode = reference_structure.sites.get_coordinate_mode()
		original_displaced_coordinate_mode = displaced_structure.sites.get_coordinate_mode()

		reference_structure.convert_sites_to_coordinate_mode(displacement_coordinate_mode)
		displaced_structure.convert_sites_to_coordinate_mode(displacement_coordinate_mode)


		for i, reference_site in enumerate(reference_structure.sites):
			for j in range(3):
				displaced_structure.sites[i]['position'][j] = reference_site['position'][j] + displacement_vector[j + i*3]


		displaced_structure.convert_sites_to_coordinate_mode(original_displaced_coordinate_mode)
		reference_structure.convert_sites_to_coordinate_mode(original_reference_coordinate_mode)

		return displaced_structure


	@staticmethod
	def no_vector_in_set_is_in_span_of_others(displacement_vector_instances_list):
		"""
		Returns true if no vector in displacement_vector_instances_list can be described by any other set of vectors 
		in displacement_vector_instances_list times coefficients.

		displacement_vector_instances_list should look like [displacement_vector_instance_1, displacement_vector_instance_2
		"""

		if len(displacement_vector_instances_list) == 0:
			raise Exception("There must be at least one veector in displacement_vector_instances_list", displacement_vector_instances_list)


		vector_matrix = []

		for displacement_vector_instance in displacement_vector_instances_list:
			vector_matrix.append(np.array(displacement_vector_instance.to_list()))

		np_vector_matrix = np.transpose(vector_matrix)

		rank = np.linalg.matrix_rank(vector_matrix, tol=1e-12) #tol is important, but emperically set here - controls threshold below which values are considered zero in the SVD

		return rank == len(displacement_vector_instances_list)