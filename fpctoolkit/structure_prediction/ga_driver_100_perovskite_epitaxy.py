import copy
import random

from fpctoolkit.structure_prediction.ga_driver import GADriver
from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.structure.lattice import Lattice
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.structure_prediction.individual import Individual
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.site_collection import SiteCollection
from fpctoolkit.structure.site import Site
from fpctoolkit.structure.site_mapping import SiteMapping
from fpctoolkit.structure.site_mapping_collection import SiteMappingCollection
from fpctoolkit.util.random_selector import RandomSelector
from fpctoolkit.util.vector import Vector
from fpctoolkit.util.distribution import Distribution
from fpctoolkit.util.vector_distribution import VectorDistribution

class GADriver100PerovskiteEpitaxy(GADriver):
	"""
	A GADriver used for finding minimum energy perovskite (100)-oriented film structures.
	"""


	def __init__(self, ga_input_dictionary, calculation_set_input_dictionary):
		"""
			ga_input_dictionary should additionally have species_list, epitaxial_lattice_constant (full number, not 5-atom cell equivalent),
			and supercell_dimensions_list keys and values
		"""

		super(GADriver100PerovskiteEpitaxy, self).__init__(ga_input_dictionary, calculation_set_input_dictionary)

		self.structure_creation_id_string = None #will track how the individual's structure was created
		self.parent_structures_list = None
		self.parent_paths_list = None
		

		if not (self.ga_input_dictionary['supercell_dimensions_list'][0] == self.ga_input_dictionary['supercell_dimensions_list'][1]):
			raise Exception("For (100) epitaxial conditions, Nx must = Ny supercell dimensions. Other behavior not yet supported")



	def create_new_individual(self, individual_path, population_of_last_generation, generation_number):
		"""
		This method will create (and return) a new individual whose initial structure was created by randomly chosen means (heredity, random, mutate, ...etc.)
		"""

		initial_structure = self.get_structure(population_of_last_generation, generation_number)

		relaxation = VaspRelaxation(path=individual_path, initial_structure=initial_structure, input_dictionary=copy.deepcopy(self.calculation_set_input_dictionary))

		return Individual(calculation_set=relaxation, structure_creation_id_string=self.structure_creation_id_string, parent_structures_list=self.parent_structures_list, parent_paths_list=self.parent_paths_list)




	def get_random_structure(self, population_of_last_generation):

		A_type = self.ga_input_dictionary['species_list'][0]
		B_type = self.ga_input_dictionary['species_list'][1]
		X_type = self.ga_input_dictionary['species_list'][2]

		Nx = self.ga_input_dictionary['supercell_dimensions_list'][0]
		Ny = self.ga_input_dictionary['supercell_dimensions_list'][1]
		Nz = self.ga_input_dictionary['supercell_dimensions_list'][2]

		a = self.ga_input_dictionary['epitaxial_lattice_constant']
		unit_cell_a = a/Nx

		c = ( a * Nz ) / Nx ##############################eventually base c off of a good volume

		lattice = [[a, 0.0, 0.0], [0.0, a, 0.0], [0.0, 0.0, c]]

		structure = Perovskite(supercell_dimensions=self.ga_input_dictionary['supercell_dimensions_list'], lattice=lattice, species_list=self.ga_input_dictionary['species_list'])


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
			strain_stdev = 0.04
		elif event_index == 1:
			shear_factor = 0.2
			strain_stdev = 0.08
		elif event_index == 2:
			shear_factor = 0.7
			strain_stdev = 0.1

		probabilities_list = [0.05, 0.15, 0.8]
		random_selector = RandomSelector(probabilities_list)
		event_index = random_selector.get_event_index()


		if event_index == 0:
			"""
			A and X sites relatively static - explore B-cation arrangements
			"""

			A_site_curvature_parameter = 0.1
			A_site_max_displacement = 0.15*unit_cell_a
			A_bell = True

			B_site_curvature_parameter = 2.5
			B_site_max_displacement = 0.3*unit_cell_a
			B_bell = True

			X_site_curvature_parameter = 0.4
			X_site_max_displacement = 0.2*unit_cell_a
			X_bell = True

			AA_minimum_distance = 2.0
			AB_minimum_distance = 1.5
			BB_minimum_distance = 1.8
			AX_minimum_distance = 1.2
			BX_minimum_distance = 1.2
			XX_minimum_distance = 1.2

		elif event_index == 1:
			"""
			A sites and B sites fairly static - X sites very random. Trying to find octahedral rotations or tetrahedral or other bonding.
			Also, focus is placed on keeping A sites and B sites spread from each other
			"""

			A_site_curvature_parameter = 0.7
			A_site_max_displacement = 0.15*unit_cell_a
			A_bell = True

			B_site_curvature_parameter = 0.8
			B_site_max_displacement = 0.3*unit_cell_a
			B_bell = True

			X_site_curvature_parameter = 3.0
			X_site_max_displacement = 0.4*unit_cell_a
			X_bell = False #encourage X atoms to be away from perfect perov sites

			AA_minimum_distance = 1.7
			AB_minimum_distance = 1.7
			BB_minimum_distance = 1.7
			AX_minimum_distance = 1.0
			BX_minimum_distance = 1.0
			XX_minimum_distance = 1.7

		elif event_index == 2:
			"""
			Basic random
			"""

			A_site_curvature_parameter = 0.8
			A_site_max_displacement = 0.35*unit_cell_a
			A_bell = True

			B_site_curvature_parameter = 2.0
			B_site_max_displacement = 0.5*unit_cell_a
			B_bell = True

			X_site_curvature_parameter = 2.0
			X_site_max_displacement = 0.5*unit_cell_a
			X_bell = True

			AA_minimum_distance = 1.4
			AB_minimum_distance = 1.0
			BB_minimum_distance = 1.0
			AX_minimum_distance = 0.8
			BX_minimum_distance = 0.8
			XX_minimum_distance = 0.8


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

		structure.lattice.randomly_strain(stdev=strain_stdev, mask_array=[[0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 1.0]])

		structure.displace_site_positions_with_minimum_distance_constraints(displacement_vector_distribution_function_dictionary_by_type, minimum_atomic_distances_nested_dictionary_by_type)
	


		self.structure_creation_id_string = 'random_standard_second_type_' + str(event_index)
		self.parent_structures_list = None

		return structure





	def get_mated_structure(self, population_of_last_generation):

		individual_1 = population_of_last_generation.get_individual_by_deterministic_tournament_selection(N=3)
		individual_2 = population_of_last_generation.get_individual_by_deterministic_tournament_selection(N=3, avoid_individuals_list=[individual_1])

		self.parent_structures_list = [copy.deepcopy(individual_1.final_structure), copy.deepcopy(individual_2.final_structure)]
		self.parent_paths_list = [individual_1.calculation_set.path, individual_2.calculation_set.path]
		site_mapping_collections_list = []

		for i, parent_structure in enumerate(self.parent_structures_list):
			print "Parent structure " + str(i+1)

			perovskite_reference_structure = Perovskite(supercell_dimensions=self.ga_input_dictionary['supercell_dimensions_list'], lattice=parent_structure.lattice, species_list=self.ga_input_dictionary['species_list'])

			perovskite_reference_structure.convert_sites_to_direct_coordinates()
			parent_structure.convert_sites_to_direct_coordinates()

			parent_structure.sites.shift_direct_coordinates([random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)])


			#This aligns the lattices - sloppy but it works...figure out a better way later
			for align_try_count in range(21):
				if align_try_count == 20:
					raise Exception("Cannot align crystal to perfect perovskite")

				site_mapping_collection = SiteMappingCollection(perovskite_reference_structure.sites, parent_structure.sites, lattice=parent_structure.lattice)
				average_displacement_vector = site_mapping_collection.get_average_displacement_vector()
				print average_displacement_vector
				site_mapping_collection.shift_sites_to_minimize_average_distance() #this shifts parent_struct's sites too because sites passed by reference

				converged = True
				for j in range(3):
					if abs(average_displacement_vector[j]) > 0.00001:
						converged = False

				if converged:
					break

			site_mapping_collections_list.append(site_mapping_collection)



		#This should be a separately inputted block controlling how interpolation is run
		if self.ga_input_dictionary['supercell_dimensions_list'][0] == 2:
			discrete_interpolation_values = [1.0, 0.8, 0.0, 0.2] #one for each plane of perov atoms
		if self.ga_input_dictionary['supercell_dimensions_list'][0] == 4:
			discrete_interpolation_values = [1.0, 1.0, 1.0, 0.8, 0.0, 0.0, 0.0, 0.2]

		def interpolation_function_da(da, db, dc):
			transition_increment = 0.5/self.ga_input_dictionary['supercell_dimensions_list'][0] #distance between perf perov planes in a direction
			transition_index = int(da/transition_increment)

			return discrete_interpolation_values[transition_index]

		def interpolation_function_db(da, db, dc):
			return interpolation_function_da(db, da, dc)

		if random.uniform(0.0, 1.0) >= 0.5:
			interpolation_function_1 = interpolation_function_da
		else:
			interpolation_function_1 = interpolation_function_db

		def interpolation_function_2(da, db, dc):
			return 1.0 - interpolation_function_1(da, db, dc)
		###################################################################################



		#make this a randomly weighted-average at some point
		averaged_lattice = Lattice.average(self.parent_structures_list[0].lattice, self.parent_structures_list[1].lattice)

		interpolated_sites_1 = site_mapping_collections_list[0].get_interpolated_site_collection(perovskite_reference_structure.sites, interpolation_function_1)
		interp_struct_1 = Structure(sites=interpolated_sites_1, lattice=averaged_lattice)

		interpolated_sites_2 = site_mapping_collections_list[1].get_interpolated_site_collection(interpolated_sites_1, interpolation_function_2)
		interp_struct_2 = Structure(sites=interpolated_sites_2, lattice=averaged_lattice)


		self.structure_creation_id_string = 'mating_interpolated_fixed'

		return interp_struct_2