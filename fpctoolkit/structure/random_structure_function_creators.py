#from fpctoolkit.structure.random_structure_function_creators import 

from fpctoolkit.structure.perovskite import Perovskite

"""
These functions should return functions that, when called, return a randomly generated structure.
"""



def get_random_perovskite_structure_generator(species_list, supercell_dimensions_list):
	"""
	Returns a function that, when called, produces a random perovskite with species_list as its atoms and supercell_dimensions as
	its supercell dimensions.
	"""

	A_type = species_list[0]
	B_type = species_list[1]
	X_type = species_list[2]

	Nx = self.ga_input_dictionary['supercell_dimensions_list'][0]
	Ny = self.ga_input_dictionary['supercell_dimensions_list'][1]
	Nz = self.ga_input_dictionary['supercell_dimensions_list'][2]

	a = self.ga_input_dictionary['epitaxial_lattice_constant']
	unit_cell_a = a/Nx

	c = ( unit_cell_a * Nz ) ##############################eventually base c off of a good volume

	lattice = [[a, 0.0, 0.0], [0.0, a, 0.0], [0.0, 0.0, c]]

	structure = Perovskite(supercell_dimensions=self.ga_input_dictionary['supercell_dimensions_list'], lattice=lattice, species_list=species_list)


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
	

	strain_probabilities_list = [0.5, 0.3, 0.2]
	random_selector = RandomSelector(strain_probabilities_list)
	event_index = random_selector.get_event_index()

	if event_index == 0:
		shear_factor = 0.1
		strain_stdev = 0.1
	elif event_index == 1:
		shear_factor = 0.25
		strain_stdev = 0.12
	elif event_index == 2:
		shear_factor = 0.6
		strain_stdev = 0.16


	"""
	Basic random
	"""

	A_site_curvature_parameter = 1.4
	A_site_max_displacement = 0.35*unit_cell_a
	A_bell = True

	B_site_curvature_parameter = 2.5
	B_site_max_displacement = 0.6*unit_cell_a
	B_bell = True

	X_site_curvature_parameter = 3.0
	X_site_max_displacement = 0.75*unit_cell_a
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

	distribution_function_array = [
		[unity_function, zero_function, e13_distribution.get_random_value], 
		[zero_function, unity_function, e23_distribution.get_random_value], 
		[zero_function, zero_function, e33_distribution.get_random_value]
		]

	structure.lattice.randomly_strain(distribution_function_array=distribution_function_array)

	StructureManipulator.displace_site_positions_with_minimum_distance_constraints(structure, displacement_vector_distribution_function_dictionary_by_type, minimum_atomic_distances_nested_dictionary_by_type)



	self.structure_creation_id_string = 'random'
	self.parent_structures_list = None
	self.parent_paths_list = None

	return structure