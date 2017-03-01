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

class GADriver100PerovskiteEpitaxy(GADriver):


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


	def get_new_individual(self, individual_path, population_of_last_generation, generation_number):
		"""
		Main workhorse - supplies an individual by randomly chosen means (heredity, random, mutate, ...etc.)
		"""

		initial_structure = self.get_structure(population_of_last_generation, generation_number)

		relaxation = VaspRelaxation(path=individual_path, initial_structure=initial_structure, input_dictionary=copy.deepcopy(self.calculation_set_input_dictionary))

		#package this with path and input_dict in calc set (relax) and return as individual

		return Individual(calculation_set=relaxation, structure_creation_id_string=self.structure_creation_id_string, parent_structures_list=self.parent_structures_list, parent_paths_list=self.parent_paths_list)

	def get_random_structure(self, population_of_last_generation):

		Nx = self.ga_input_dictionary['supercell_dimensions_list'][0]
		Ny = self.ga_input_dictionary['supercell_dimensions_list'][1]
		Nz = self.ga_input_dictionary['supercell_dimensions_list'][2]

		a = self.ga_input_dictionary['epitaxial_lattice_constant']
		unit_cell_a = a/Nx

		c = ( a * Nz ) / Nx ##############################eventually base c off of a good volume

		lattice = [[a, 0.0, 0.0], [0.0, a, 0.0], [0.0, 0.0, c]]

		structure = Perovskite(supercell_dimensions=self.ga_input_dictionary['supercell_dimensions_list'], lattice=lattice, species_list=self.ga_input_dictionary['species_list'])



		
		probabilities_list = [0.1, 0.6, 0.3]
		random_selector = RandomSelector(probabilities_list)
		event_index = random_selector.get_event_index()


		minimum_atomic_distance_list = [1.5, 1.5, 1.3]
		#The direction of displacement is always spherically uniformly distributed, but we can control the
		#mean radius of this sphere, the standard deviation of this sphere radius, and the max limiting 
		#outer shell of the sphere. These factors are given for A, B, and O atoms separately.

		if event_index == 0: #very close to perfect perovskite, little strain, mostly B-cation displacements
			shear_factor = 0.2
			strain_stdev = 0.06

			mean_displacement_magnitude_list = [0.0*unit_cell_a, 0.15*unit_cell_a, 0.0*unit_cell_a]
			displacement_stdev_list = [0.1*unit_cell_a, 0.2*unit_cell_a, 0.15*unit_cell_a]
			max_atomic_displacement_list = [0.3*(0.7071*unit_cell_a), 0.7*(0.5*unit_cell_a), 0.4*(0.7071*unit_cell_a)]

			minimum_atomic_distance_list = [1.5, 1.2, 1.2] #this controls the min dist when A is displaced, B is displaced, etc.
		elif event_index == 1: #A lot of displacement all alround, little shear strain
			shear_factor = 0.1
			strain_stdev = 0.08

			mean_displacement_magnitude_list = [0.0*unit_cell_a, 0.0*unit_cell_a, 0.0*unit_cell_a]
			displacement_stdev_list = [0.22*unit_cell_a, 0.4*unit_cell_a, 0.4*unit_cell_a]
			max_atomic_displacement_list = [0.3*(0.7071*unit_cell_a), 1.0*(0.5*unit_cell_a), 0.9*(0.7071*unit_cell_a)]
			minimum_atomic_distance_list = [1.3, 1.2, 1.2]
		elif event_index == 2: #A lot of displacement all around, significant shear
			shear_factor = 0.5
			strain_stdev = 0.12

			mean_displacement_magnitude_list = [0.0*unit_cell_a, 0.0*unit_cell_a, 0.0*unit_cell_a]
			displacement_stdev_list = [0.2*unit_cell_a, 0.45*unit_cell_a, 0.45*unit_cell_a]
			max_atomic_displacement_list = [0.3*(0.7071*unit_cell_a), 1.0*(0.5*unit_cell_a), 0.9*(0.7071*unit_cell_a)]
			minimum_atomic_distance_list = [1.3, 1.2, 1.2]


		structure.lattice.randomly_strain(stdev=strain_stdev, mask_array=[[0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 1.0]])



		#iterate through each type (A, B, O) and apply the specific random distributions when displacing
		for i in range(3):
			structure.randomly_displace_site_positions(stdev=displacement_stdev_list[i], enforced_minimum_atomic_distance=minimum_atomic_distance_list[i], 
				max_displacement_distance=max_atomic_displacement_list[i], mean=mean_displacement_magnitude_list[i], types_list=self.ga_input_dictionary['species_list'][i])
		

		self.structure_creation_id_string = 'random_standard_type_' + str(event_index)
		self.parent_structures_list = None

		return structure





	def get_mated_structure(self, population_of_last_generation):

		#select parents from population first#################################

		#parent_structure_1 = self.get_random_structure(None)
		#parent_structure_2 = self.get_random_structure(None)

		#parent_structure_1 = Structure(file_path="C:\Users\Tom\Documents\Coding\python_work\workflow_test/20_atom_parent_1.vasp")
		#parent_structure_2 = Structure(file_path="C:\Users\Tom\Documents\Coding\python_work\workflow_test/20_atom_parent_2.vasp")

		#parent_structure_2 = Perovskite(supercell_dimensions=self.ga_input_dictionary['supercell_dimensions_list'], lattice=parent_structure_2.lattice, species_list=self.ga_input_dictionary['species_list'])
		#parent_structure_2.sites.shift_direct_coordinates([0.25, 0.25, 0.25])


		######NOTE: Should avoid selecting combos that have already mated?

		individual_1 = population_of_last_generation.get_individual_by_deterministic_tournament_selection(N=3)
		individual_2 = population_of_last_generation.get_individual_by_deterministic_tournament_selection(N=3, avoid_individuals_list=[individual_1])

		self.parent_structures_list = [individual_1.final_structure, individual_2.final_structure]
		self.parent_paths_list = [individual_1.calculation_set.path, individual_2.calculation_set.path]
		site_mapping_collections_list = []

		for i, parent_structure in enumerate(self.parent_structures_list):
			print "Parent structure " + str(i+1)
			#parent_structure.to_poscar_file_path("C:\Users\Tom\Documents\Coding\python_work\workflow_test/parent_initial_"+str(i+1)+".vasp")

			perovskite_reference_structure = Perovskite(supercell_dimensions=self.ga_input_dictionary['supercell_dimensions_list'], lattice=parent_structure.lattice, species_list=self.ga_input_dictionary['species_list'])
			#perovskite_reference_structure.to_poscar_file_path("C:\Users\Tom\Documents\Coding\python_work\workflow_test/ref_"+str(i+1)+".vasp")
			perovskite_reference_structure.convert_sites_to_direct_coordinates()
			parent_structure.convert_sites_to_direct_coordinates()

			parent_structure.sites.shift_direct_coordinates([random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)])
			#parent_structure.to_poscar_file_path("C:\Users\Tom\Documents\Coding\python_work\workflow_test/parent_initial_rnd_shift_"+str(i+1)+".vasp")

			#This aligns the lattices - sloppy but it works...figure out a better way later
			#Should change to be done until average disp vec components are all within epsilon of 0.0 - throw error if can't
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

			#parent_structure.to_poscar_file_path("C:\Users\Tom\Documents\Coding\python_work\workflow_test/parent_shifted_"+str(i+1)+".vasp")

			#

			#################
			# if i == 1:
			# 	structs = site_mapping_collection.get_interpolated_structure_list()

			# 	for j, struct in enumerate(structs):
			# 		struct.to_poscar_file_path("C:\Users\Tom\Documents\Coding\python_work\workflow_test/interp_" + str(j) + ".vasp")
			#################

			site_mapping_collections_list.append(site_mapping_collection)

			#parent_structure.to_poscar_file_path("C:\Users\Tom\Documents\Coding\python_work\workflow_test/parent_shifted_"+str(i+1)+".vasp")


		if self.ga_input_dictionary['supercell_dimensions_list'][0] == 2:
			discrete_interpolation_values = [1.0, 0.8, 0.0, 0.2] #one for each plane of perov atoms
		if self.ga_input_dictionary['supercell_dimensions_list'][0] == 4:
			discrete_interpolation_values = [1.0, 1.0, 0.9, 0.75, 0.0, 0.0, 0.1, 0.75]

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


		#make this a weighted-average at some point
		averaged_lattice = Lattice.average(self.parent_structures_list[0].lattice, self.parent_structures_list[1].lattice)

		interpolated_sites_1 = site_mapping_collections_list[0].get_interpolated_site_collection(perovskite_reference_structure.sites, interpolation_function_1)
		interp_struct_1 = Structure(sites=interpolated_sites_1, lattice=averaged_lattice)
		#interp_struct_1.to_poscar_file_path("C:\Users\Tom\Documents\Coding\python_work\workflow_test/parent_interp_1.vasp")

		interpolated_sites_2 = site_mapping_collections_list[1].get_interpolated_site_collection(interpolated_sites_1, interpolation_function_2)
		interp_struct_2 = Structure(sites=interpolated_sites_2, lattice=averaged_lattice)
		#interp_struct_2.to_poscar_file_path("C:\Users\Tom\Documents\Coding\python_work\workflow_test/parent_interp_2.vasp")


		self.structure_creation_id_string = 'mating_interpolated'

		return interp_struct_2