#from fpctoolkit.structure.structure_generator import StructureGenerator

from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.util.random_selector import RandomSelector
from fpctoolkit.util.math.distribution import Distribution
from fpctoolkit.util.math.vector_distribution import VectorDistribution
from fpctoolkit.util.math.vector import Vector
from fpctoolkit.structure.structure_manipulator import StructureManipulator
from fpctoolkit.structure.lattice import Lattice



class StructureGenerator(object):
	"""
	Defines static methods useful for generating random structures. These methods fall into two categories:

	1. Methods that return functions that, when called with no arguments, return a randomly generated structure.
	2. Helper methods for creating the functions of the first type.
	"""

	@staticmethod
	def get_random_perovskite_structure_generator(species_list=None, primitive_cell_lattice_constant=None, supercell_dimensions_list=None):
		"""
		Returns a function that, when called with no arguments, produces a random perovskite with species_list as its atoms and supercell_dimensions as
		its supercell dimensions. 

		primitive_cell_lattice_constant is length (in Angstroms) of the perovskite cubic lattice vector
		"""

		def structure_generator():
			return StructureGenerator.get_random_perovskite_structure(species_list, primitive_cell_lattice_constant, supercell_dimensions_list)

		return structure_generator #####???????????????!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!this whole func should be some util call that takes in a function and args list and returns an argument-less function


	@staticmethod
	def get_random_perovskite_structure(species_list=None, primitive_cell_lattice_constant=None, supercell_dimensions_list=None, strain_distribution_function_array=None):
		"""
		Returns a random perovskite structure with species_list as its atom types and supercell_dimensions as
		its supercell dimensions. 

		primitive_cell_lattice_constant is length (in Angstroms) of the perovskite cubic lattice vector in a 5-atom unit cell
		"""

		Nx = supercell_dimensions_list[0]
		Ny = supercell_dimensions_list[1]
		Nz = supercell_dimensions_list[2]

		a = primitive_cell_lattice_constant*Nx
		b = primitive_cell_lattice_constant*Ny
		c = primitive_cell_lattice_constant*Nz 

		


		##############Move this chunk somewhere else - this func should just take in the strain distribution function array#####################################

		e33_average = 1.0
		e33_spread = 0.2
		min_e33 = e33_average - e33_spread
		max_e33 = e33_average + e33_spread
		e33_distribution_function = lambda x: (e33_spread - (abs(e33_average-x)))**0.4 #very broad bell shape max at 1.0, 0.0 at edges
		e33_distribution = Distribution(e33_distribution_function, min_e33, max_e33)


		e13_average = 0.0
		e13_spread = 0.2
		min_e13 = e13_average - e13_spread
		max_e13 = e13_average + e13_spread
		e13_distribution_function = lambda x: (e13_spread - (abs(e13_average-x)))**0.8 #somewhat broad bell shape max at 0.0, 0.0 at edges
		e13_distribution = Distribution(e13_distribution_function, min_e13, max_e13)


		e23_average = 0.0
		e23_spread = 0.2
		min_e23 = e23_average - e23_spread
		max_e23 = e23_average + e23_spread
		e23_distribution_function = lambda x: (e23_spread - (abs(e23_average-x)))**0.8 #somewhat broad bell shape max at 0.0, 0.0 at edges
		e23_distribution = Distribution(e23_distribution_function, min_e23, max_e23)

		zero_function = lambda : 0.0
		unity_function = lambda : 1.0

		strain_distribution_function_array = [
			[unity_function, zero_function, e13_distribution.get_random_value], 
			[zero_function, unity_function, e23_distribution.get_random_value], 
			[zero_function, zero_function, e33_distribution.get_random_value]
			]

		###################################################################################################################################################


		lattice = Lattice([[a, 0.0, 0.0], [0.0, b, 0.0], [0.0, 0.0, c]])
		structure = Perovskite(supercell_dimensions=supercell_dimensions_list, lattice=lattice, species_list=species_list)
		structure.lattice.randomly_strain(distribution_function_array=strain_distribution_function_array)

		##############################################################this stuff as well should be factored out - also take in 
		#displacement_vector_distribution_function_dictionary_by_type and minimum_atomic_distances_nested_dictionary_by_type

		def envelope_function(curvature_parameter, max_displacement_distance, bell=True):
			"""
			for bell == True:
				Get a curve that is high at 0, lower as you get away from 0
				curvature_parameter: closer to 0 means sharper peak at 0, closer to 3 or more, very constant until sharp drop to 0 at max_disp_dist
			for bell == False:
				Curve is 0 at 0, highest at max_disp_dist
				curvature_parameter: closer to 0 means curve gets to large value faster (less of an abyss around 0), larger means sharp increase near max_disp
			"""

			if bell:
				offset = 1.0
				sign = -1.0
			else:
				offset = 0.0
				sign = 1.0


			if max_displacement_distance == 0:
				return lambda x: 1.0
			else:
				return lambda x: offset + sign*((x**curvature_parameter)/(max_displacement_distance**curvature_parameter))


		A_type = species_list[0]
		B_type = species_list[1]
		X_type = species_list[2]


		A_site_curvature_parameter = 1.4
		A_site_max_displacement = 0.35*primitive_cell_lattice_constant
		A_bell = True

		B_site_curvature_parameter = 2.5
		B_site_max_displacement = 0.6*primitive_cell_lattice_constant
		B_bell = True

		X_site_curvature_parameter = 3.0
		X_site_max_displacement = 0.75*primitive_cell_lattice_constant
		X_bell = True

		AA_minimum_distance = 1.2
		AB_minimum_distance = 0.8
		BB_minimum_distance = 0.8
		AX_minimum_distance = 0.6
		BX_minimum_distance = 0.6
		XX_minimum_distance = 0.6


		A_site_vector_magnitude_distribution_function = Distribution(envelope_function(A_site_curvature_parameter, A_site_max_displacement, A_bell), 0.0, A_site_max_displacement).get_random_value
		B_site_vector_magnitude_distribution_function = Distribution(envelope_function(B_site_curvature_parameter, B_site_max_displacement, B_bell), 0.0, B_site_max_displacement).get_random_value
		X_site_vector_magnitude_distribution_function = Distribution(envelope_function(X_site_curvature_parameter, X_site_max_displacement, X_bell), 0.0, X_site_max_displacement).get_random_value

		A_site_vector_distribution_function = VectorDistribution(Vector.get_random_unit_vector, A_site_vector_magnitude_distribution_function)
		B_site_vector_distribution_function = VectorDistribution(Vector.get_random_unit_vector, B_site_vector_magnitude_distribution_function)
		X_site_vector_distribution_function = VectorDistribution(Vector.get_random_unit_vector, X_site_vector_magnitude_distribution_function)

		displacement_vector_distribution_function_dictionary_by_type = {
			A_type: A_site_vector_distribution_function.get_random_vector,
			B_type: B_site_vector_distribution_function.get_random_vector,
			X_type: X_site_vector_distribution_function.get_random_vector
		}

		minimum_atomic_distances_nested_dictionary_by_type = {
			A_type: {A_type: AA_minimum_distance, B_type: AB_minimum_distance, X_type: AX_minimum_distance},
			B_type: {A_type: AB_minimum_distance, B_type: BB_minimum_distance, X_type: BX_minimum_distance},
			X_type: {A_type: AX_minimum_distance, B_type: BX_minimum_distance, X_type: XX_minimum_distance}
		}


		##########################################################################################################################


		StructureManipulator.displace_site_positions_with_minimum_distance_constraints(structure, displacement_vector_distribution_function_dictionary_by_type, minimum_atomic_distances_nested_dictionary_by_type)

		return structure