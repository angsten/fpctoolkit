import numpy as np
import copy

from fpctoolkit.io.file import File
from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.structure.site import Site
from fpctoolkit.structure.lattice import Lattice
from fpctoolkit.structure.site_collection import SiteCollection
from fpctoolkit.util.vector import Vector

class Structure(object):
	"""
	Abstract crystal structure class.

	Holds 2D array for lattice and a SiteCollection instance
	Compatible with poscar file class only for now.
	"""
	def __init__(self, file_path=None, lattice=None, sites=None):

		if file_path: #load from file (only poscar supported for now)
			self.from_poscar_file_path(file_path)
		else:
			self.lattice = Lattice(lattice)

			if isinstance(sites, SiteCollection):
				self.sites = sites
			else:
				raise Exception("sites must be of SiteColleciton type")

	def __str__(self):
		return str(self.lattice) + "\n".join(str(site) for site in self.sites) + "\n"


	def from_poscar_file_path(self, file_path):
		poscar = Poscar(file_path)
		self.lattice = Lattice(poscar.lattice)
		self.sites = SiteCollection()

		species_index = 0
		for i, specie in enumerate(poscar.species_list):
			for j in range(poscar.species_count_list[i]):
				new_site = Site()
				new_site['coordinate_mode'] = poscar.coordinate_mode
				new_site['position'] = poscar.coordinates[species_index]
				new_site['type'] = specie

				self.sites.append(new_site)

				species_index += 1


	def to_poscar_file_path(self, file_path):
		lattice = self.lattice.to_array()
		species_list = self.sites.get_species_list()
		species_count_list = self.sites.get_species_count_list()
		coordinate_mode = self.sites.get_sorted_list()[0]['coordinate_mode']
		coordinates = self.sites.get_coordinates_list()

		for site in self.sites:
			if site['coordinate_mode'] != coordinate_mode:
				raise Exception("Not all coordinate modes in structure are consistent. Cannot write to poscar file.")

		poscar = Poscar(None, lattice, species_list, species_count_list, coordinate_mode, coordinates)
		poscar.write_to_path(file_path)

	def get_species_list(self):
		return self.sites.get_species_list()

	def get_species_count_list(self):
		return self.sites.get_species_count_list()

	def get_coordinates_list(self):
		return self.sites.get_coordinates_list()

	@property
	def site_count(self):
		return len(self.sites)

	def convert_sites_to_cartesian_coordinates(self):
		"""
		Takes any site in sites that is in direct coordinates and changes
		its position and coordinate mode to be in cartesian coordinate system
		"""

		for site in self.sites:
			site.convert_to_cartesian_coordinates(self.lattice)

	def convert_sites_to_direct_coordinates(self):
		"""Takes any site in sites that is in cartesian coordinates and changes
		its position and coordinate mode to be in direct coordinate system
		"""

		for site in self.sites:
			site.convert_to_direct_coordinates(self.lattice)

	def get_supercell(self, supercell_dimensions_list):
		"""
		Returns new structure that is a supercell of this structure (self)
		Argument supercell_dimensions_list looks like [1,3,4]
		"""

		if not len(supercell_dimensions_list) == 3:
			raise Exception("Argument supercell_dimensions_list must be of length 3")

		for dimension in supercell_dimensions_list:
			if not int(dimension) == dimension:
				raise Exception("Only integer values accepted for supercell dimension factors.")

		self.convert_sites_to_direct_coordinates()

		new_lattice = self.lattice.get_super_lattice(supercell_dimensions_list)
		new_sites = SiteCollection()

		for original_site in self.sites:
			for a in range(supercell_dimensions_list[0]):
				for b in range(supercell_dimensions_list[1]):
					for c in range(supercell_dimensions_list[2]):
						a_frac = float(a)/float(supercell_dimensions_list[0])
						b_frac = float(b)/float(supercell_dimensions_list[1])
						c_frac = float(c)/float(supercell_dimensions_list[2])

						new_site = copy.deepcopy(original_site)
						old_position = original_site['position']
						new_site['position'] = [old_position[0]/supercell_dimensions_list[0]+a_frac, old_position[1]/supercell_dimensions_list[1]+b_frac, old_position[2]/supercell_dimensions_list[2]+c_frac]
						new_sites.append(new_site)


		return Structure(lattice=new_lattice, sites=new_sites)


	def displace_site_positions_with_minimum_distance_constraints(self, displacement_vector_distribution_function_dictionary_by_type=None, minimum_atomic_distances_nested_dictionary_by_type=None):
		"""
		Displace the atoms of this structure rusing the specified probability distribution functions for each atom type.
		This method preserves the overall distribution rho(x1, y1, z1, x2, y2, z2, ...) resulting from multiplication
		of the indiviidual independent atomic distributions but with the regions of atoms too close (distance < min_atomic_dist) set to rho = 0.
		This just renormalizes the other parts of the distribution space so integral of rho sums to unity.

		displacement_vector_distribution_function_dictionary_by_type should look like:
		{
			'Ba': dist_func_1(), #dist funcs are methods that return cartesian vectors in angstroms ([x, y, z]) using distributions of your choosing
			'Ti': dist_func_2(),
			...
		}

		minimum_atomic_distances_nested_dictionary_by_type is in angstroms and looks like:
		{
			'Ba': {'Ti': 1.2, 'O': 1.4},
			'Ti': {'Ba': 1.2, 'O': 1.3},
			'O':  {'Ba': 1.4, 'Ti': 1.3}
		}

		Where calling any of the dist_funcs must return a displacement vector that uses cartesian coordinates and angstroms as its units. 
		If no function is given for a type, the zero vector function is used.

		Structures are randomly displaced until no two atoms are within minimum_atomic_distance under periodic boundary conditions
		"""

		original_structure = copy.deepcopy(self)

		for try_count in range(100):
			print "try is ", try_count

			self.displace_site_positions(displacement_vector_distribution_function_dictionary_by_type)

			if self.any_sites_are_too_close(minimum_atomic_distances_nested_dictionary_by_type):
				self = copy.deepcopy(original_structure)
			else:
				return

		raise Exception("Could not displace this structure while satisfying the given constraints")



	def displace_site_positions(self, displacement_vector_distribution_function_dictionary_by_type=None):
		"""
		Inner loop helper function for displace_site_positions_with_minimum_distance_constraint
		"""

		if (displacement_vector_distribution_function_dictionary_by_type == None) or len(displacement_vector_distribution_function_dictionary_by_type) == 0:
			raise Exception("A displacement vector function for at least one atom type must be specified.")

		for species_type in displacement_vector_distribution_function_dictionary_by_type:
			if not species_type in self.sites:
				raise Exception("Strucuture does not have a site of type " + str(species_type))

		#If a distribution function is not provided for a given type, set that type's function to the zero vector function
		for species_type in self.sites:
			if not species_type in displacement_vector_distribution_function_dictionary_by_type:
				displacement_vector_distribution_function_dictionary_by_type[species_type] = lambda: [0, 0, 0]


		for species_type in self.sites:
			for site in self.sites[species_type]:

				#get a displacement vector (in cartesian coordinates)
				displacement_vector = displacement_vector_distribution_function_dictionary_by_type[species_type]()

				if site['coordinate_mode'] == 'Direct':
					displacement_vector = Vector.get_in_direct_coordinates(displacement_vector, self.lattice)

					site.displace(displacement_vector)


	def any_sites_are_too_close(self, minimum_atomic_distances_nested_dictionary_by_type, nearest_neighbors_max=3):
		"""
		Returns True if any two sites in this structure are within minimum_atomic_distance (angstroms) of each other.
		Min distances is different for each type pair, as specified by the input dictionary.
		nearest_neighbors_max controls how many nearest neighbor cell images to search.	

		minimum_atomic_distances_nested_dictionary_by_type is in angstroms and looks like:
		{
			'Ba': {'Ti': 1.2, 'O': 1.4},
			'Ti': {'Ba': 1.2, 'O': 1.3},
			'O':  {'Ba': 1.4, 'Ti': 1.3}
		}
		"""

		sites_list = self.sites.get_sorted_list()

		for site_1_index in range(len(sites_list)):
			for site_2_index in range(site_1_index+1, len(sites_list)):
				site_1 = sites_list[site_1_index]
				site_2 = sites_list[site_2_index]

				minimum_atomic_distance = minimum_atomic_distances_nested_dictionary_by_type[site_1['type']][site_2['type']]

				if site_pair_is_too_close(site_1, site_2, minimum_atomic_distance, nearest_neighbors_max):
					return True

		return False



	def site_pair_is_too_close(self, site_1, site_2, minimum_atomic_distance, nearest_neighbors_max=3):
		"""
		Returns true if site_1 position is within minimum_atomic_distance of site_2 position under periodic boundary conditions.
		nearest_neighbors_max controls how many nearest neighbor cell images to search. Higher means higher accuracy in heavily sheared structures
		"""

		site_1.convert_to_direct_coordinates(self.lattice)
		site_2.convert_to_direct_coordinates(self.lattice)

		distance = Vector.get_minimum_distance_between_two_periodic_points(site_1['position'], site_2['position'], self.lattice, nearest_neighbors_max)

		return (distance < minimum_atomic_distance)



	def any_sites_are_too_close_to_site(self, test_site, minimum_atomic_distances_nested_dictionary_by_type, nearest_neighbors_max=3):
		"""
		Returns True if any site in this structure is within minimum_atomic_distance (angstroms) of test_site.
		Minimum distance is different for each type pair, as specified in minimum_atomic_distances_nested_dictionary_by_type
		Ignores if test_site is the same object (address compared) as a site in the structure. 
		nearest_neighbors_max controls how many nearest neighbor cell images to search. Higher means higher accuracy in heavily sheared structures


		minimum_atomic_distances_nested_dictionary_by_type is in angstroms and looks like:
		{
			'Ba': {'Ti': 1.2, 'O': 1.4},
			'Ti': {'Ba': 1.2, 'O': 1.3},
			'O':  {'Ba': 1.4, 'Ti': 1.3}
		}
		"""

		####################not implemented yet

		for species_type in self.sites:
			if species_type not in minimum_atomic_distances_nested_dictionary_by_type:
				raise Exception("Minimum atomic for all pairs of types in this structure not specified.")

		self.convert_sites_to_direct_coordinates()

		test_site_fractional_coordinates = test_site['position'] if test_site['coordinate_mode'] == 'Direct' else Vector.get_in_direct_coordinates(test_site['position'], self.lattice)

		for other_site in self.sites:
			if test_site is other_site: #don't consider case where these are the same site objects
				continue

			minimum_distance = Vector.get_minimum_distance_between_two_periodic_points(test_site_fractional_coordinates, other_site['position'], self.lattice, nearest_neighbors_max)
			minimum_atomic_distance = minimum_atomic_distances_nested_dictionary_by_type[test_site['type']][other_site['type']]

			if minimum_distance < minimum_atomic_distance:
				return True

		return False

