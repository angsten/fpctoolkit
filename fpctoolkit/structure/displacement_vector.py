#from fpctoolkit.structure.displacement_vector import DisplacementVector

import numpy as np
import copy

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.structure.structure import Structure
from fpctoolkit.util.math.vector import Vector

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


	def set(self, displacement_vector_list):
		"""
		Takes in list of displacements and sets self.displacement_vector equal to this list
		"""

		if len(displacement_vector_list) != self.reference_structure.site_count*3:
			raise Exception("Length of displacement vector inputted and number of displacement degrees of freedom in reference structure do not match", len(displacement_vector_list) , 3*self.reference_structure.site_count)

		self.displacement_vector = copy.deepcopy(displacement_vector_list)


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

	def to_numpy_array(self):
		return np.asarray(self.displacement_vector)

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
	def get_instance_from_displaced_structure_relative_to_reference_structure(reference_structure, displaced_structure, coordinate_mode='Cartesian'):
		"""
		Returns a DisplacementVector instance made by comparing each atom in displaced_structure with those of reference_structure.
		The atoms are mapped to each other based on their positions in the site collection lists.
		The vector connecting two sites is the shortest one possible under periodic boundary conditions.

		The coordinate_mode argument determines whether direct fractional coordinates (unitless) or Cartesian coordinates (in Angstroms) are used to describe the displacements.
		"""

		Structure.validate(reference_structure)
		Structure.validate(displaced_structure)

		if reference_structure.site_count != displaced_structure.site_count:
			raise Exception("Site counts of two structures must be equal.", reference_structure.site_count, displaced_structure.site_count)


		lattice_1_np_array = reference_structure.lattice.to_np_array().flatten()
		lattice_2_np_array = displaced_structure.lattice.to_np_array().flatten()

		difference_array = lattice_2_np_array - lattice_1_np_array

		if np.linalg.norm(difference_array) > 1e-8:
			raise Exception("Lattice for reference and displaced structure are not equivalent. This will break the pbc shortest vector portion of this call.", difference_array)


		reference_structure = copy.deepcopy(reference_structure)
		displaced_structure = copy.deepcopy(displaced_structure)

		reference_structure.convert_sites_to_coordinate_mode('Direct')
		displaced_structure.convert_sites_to_coordinate_mode('Direct')

		displacement_vector = DisplacementVector(reference_structure=reference_structure, coordinate_mode=coordinate_mode)

		for site_index in range(reference_structure.site_count):
			reference_site = reference_structure.sites[site_index]
			displaced_site = displaced_structure.sites[site_index]

			if reference_site['type'] != displaced_site['type']:
				raise Exception("Types of two structures do not align.", reference_site['type'], displaced_site['type'])

			#if lattices of displaced and reference and not the same at this point, problems will arise here!!!!
			shortest_pbc_vector_between_sites = Vector.get_minimum_distance_between_two_periodic_points(fractional_coordinate_1=reference_site['position'], ###############setting N_max to 2 - may need to be larger for heavily sheared systems!!!
				fractional_coordinate_2=displaced_site['position'], lattice=reference_structure.lattice, N_max=2, return_vector=True)[1]

			if coordinate_mode =='Cartesian':
				shortest_pbc_vector_between_sites = Vector.get_in_cartesian_coordinates(direct_vector=shortest_pbc_vector_between_sites, lattice=reference_structure.lattice)

			for i in range(3):
				displacement_vector[site_index*3+i] = shortest_pbc_vector_between_sites[i]


		return displacement_vector




	@staticmethod
	def displace_structure(reference_structure, displacement_vector, displacement_coordinate_mode):
		"""
		Adds displacement_vector (list of floats) to the positions of the input reference structure and returns a new structure. 
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