#from fpctoolkit.phonon.normal_mode import NormalMode

import numpy as np
import copy
import math
import cmath

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.structure.structure import Structure
import fpctoolkit.util.string_util as su


class NormalMode(object):
	"""
	Represents a single normal mode in a phonon spectrum storing the q-point, band index, and eigen-displacements.
	"""

	def __init__(self, eigenvector, frequency, q_point_fractional_coordinates, band_index, primitive_cell_structure, atomic_masses_list):
		"""
		eigenvector should be a list that looks like [atom_1_x_component_of_generalized_displacement_complex_number, atom_1_y..., ..., atom_2_x, ...] -> the 
		sqrt(mass) term should be left in for each component. This vector should be a list of length Nat, where Nat is the number of atoms in the primitive cell 
		used to generate the phonon band structure.

		The q_point input argument should be a tuple of three real numbers in reduced coordinates with no factor of 2Pi, e.g. (0.5, 0.5, 0.0).

		frequency should be a complex number - if imaginary only then mode is unstable.

		band_index should start at zero and go to Nat*3-1

		atomic_masses_list should look like [atomic_1_mass, atomic_2_mass, ..., atomic_Natoms_in_cell_mass]
		"""

		complex_vector_magnitude = np.linalg.norm(eigenvector)

		basic_validators.validate_approximately_equal(complex_vector_magnitude, 1.0, tolerance=0.000001)

		basic_validators.validate_complex_number(frequency)

		if (frequency.real > 0.0) and (frequency.imag > 0.0):
			raise Exception("Frequency cannot have mixed real and imaginary components. Frequency is", frequency)

		if not len(q_point_fractional_coordinates) == 3:
			raise Exception("Qpoint argument must have three compononents. Argument is", q_point_fractional_coordinates)

		if primitive_cell_structure.site_count != len(atomic_masses_list):
			raise Exception("Length of atomic masses list and number of sites are not equal.")

		Structure.validate(primitive_cell_structure)


		self.eigenvector = eigenvector
		self.frequency = frequency
		self.q_point_fractional_coordinates = q_point_fractional_coordinates
		self.band_index = band_index
		self.primitive_cell_structure = primitive_cell_structure
		self.atomic_masses_list = atomic_masses_list

		self.eigen_displacements_list = self.get_eigen_displacements_vector()

	@property
	def unstable(self):
		return (self.frequency.imag > 0.0)

	@property
	def translational(self):
		"""
		Checks if this mode is a trivial translational mode which just shifts all atoms by equal amounts with no effect on the energy of the crystal.
		"""

		#####implement - check freq is suff close to zero and all atomic disp vecs are equal for each atom along a cartesian direction
		###also check that the qpoint is 0 0 0

		return False


	def get_eigen_displacements_vector(self):
		"""
		This method returns a new eigen vector that has the 1/sqrt(ion_mass) term factored out. The returned eigenvector
		represents the (normalized) displacement patterns in Angstroms for this mode.
		"""

		displacements_eigen_vector = copy.deepcopy(self.eigenvector)

		for i in range(len(displacements_eigen_vector)):
			displacements_eigen_vector[i] *= (1/math.sqrt(self.atomic_masses_list[(int(i/3))]))

		#now normalize vector
		vector_magnitude = np.linalg.norm(displacements_eigen_vector)

		for i in range(len(displacements_eigen_vector)):
			displacements_eigen_vector[i] *= 1/vector_magnitude

		return displacements_eigen_vector


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

		return_string = ""

		dash_spread = "-"*14

		band_string = str(self.band_index+1)

		add_string = '-' if len(band_string) == 1 else ''

		dash_string = dash_spread + str(self.q_point_fractional_coordinates) + dash_spread + "band index: " + band_string + dash_spread + add_string

		return_string += dash_string + "\n\n"


		frequency_string = str(round(self.frequency.real, 5)) if self.frequency.real > 0.0 else str(round(self.frequency.imag, 5)) + 'i'

		return_string += "Frequency: " + frequency_string + '\n\n'

		eigen_vector = self.eigen_displacements_list

		for i in range(len(eigen_vector)/3):

				f = su.pad_decimal_number_to_fixed_character_length
				rnd = 4
				padding_length = 8
				sep = "   "

				atom_str = self.primitive_cell_structure.sites[i]['type']
				if len(atom_str) == 1:
					atom_str += " "

				string = atom_str + sep + str(f(eigen_vector[3*i].real, rnd, padding_length)) + sep + str(f(eigen_vector[3*i+1].real, rnd, padding_length)) + sep + str(f(eigen_vector[3*i+2].real, rnd, padding_length)) 
				string += sep*2 + str(f(eigen_vector[3*i].imag, rnd, padding_length)) + sep + str(f(eigen_vector[3*i+1].imag, rnd, padding_length)) + sep + str(f(eigen_vector[3*i+2].imag, rnd, padding_length))

				return_string += string + '\n'


		return_string += "-"*len(dash_string) + '\n'

		return return_string

