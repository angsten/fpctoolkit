#from fpctoolkit.phonon.normal_mode import NormalMode

import numpy as np

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.structure.structure import Structure


class NormalMode(object):
	"""
	Represents a single normal mode in a phonon spectrum storing the q-point, band index, and eigen-displacements.
	"""

	def __init__(self, normalized_eigen_displacements, frequency, q_point_fractional_coordinates, band_index, primitive_cell_structure):
		"""
		normalized_eigen_displacements should be a list that looks like [atom_1_x_component_of_displacement_complex_number, atom_1_y..., ..., atom_2_x, ...] 
		and should be of length Nat, where Nat is the number of atoms in the primitive cell used to generate the phonon band structure.

		The q_point input argument should be a list of three real numbers in reduced coordinates with no factor of 2Pi, e.g. (0.5, 0.5, 0.0).
		"""

		complex_vector_magnitude = np.linalg.norm(normalized_eigen_displacements)

		basic_validators.validate_approximately_equal(complex_vector_magnitude, 1.0, tolerance=0.000001)

		basic_validators.validate_real_number(frequency)

		Structure.validate(primitive_cell_structure)

		if not len(q_point_fractional_coordinates) == 3:
			raise Exception("Qpoint argument must have three compononents. Argument is", q_point_fractional_coordinates)


		self.eigen_displacements_list = normalized_eigen_displacements
		self.frequency = frequency
		self.q_point_fractional_coordinates = q_point_fractional_coordinates
		self.band_index = band_index
		self.primitive_cell_structure = primitive_cell_structure

	@property
	def unstable(self):
		return (self.frequency < 0.0)

	@property
	def translational(self):
		"""
		Checks if this mode is a trivial translational mode which just shifts all atoms by equal amounts with no effect on the energy of the crystal.
		"""

		#####implement - check freq is suff close to one and all atomic disp vecs are equal

		return False

	def get_supercell_displacements(self, complex_amplitude, supercell_dimensions):
		"""
		Returns the set of displacements produced when applying this phonon mode to a supercell of size supercell_dimensions with amplitude complex_amplitude.
		The q_point of this normal mode must be commensurate with supercell_dimensions.

		Output: a list of real-space displacements in angstroms that looks like:

		[disp_atom_type_1_x_cell_1, disp_atom_type_1_y_cell_1, ..._z_..., ...type_1_x_cell_2, ..., ...type_1_z_cell_Ncells..., ...type_2_x_cell_1_..., ...]
		"""

		#first verify this qpoint is commensurate with the supercell dimensions (I think dim[i]*q_point[i] = integer is condition)


		pass

	def __str__(self):

		#print here
		return "under work"

