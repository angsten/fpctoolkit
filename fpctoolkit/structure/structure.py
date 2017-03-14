#from fpctoolkit.structure.structure import Structure
import numpy as np
import copy

from fpctoolkit.io.file import File
from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.structure.site import Site
from fpctoolkit.structure.lattice import Lattice
from fpctoolkit.structure.site_collection import SiteCollection
from fpctoolkit.util.vector import Vector
from fpctoolkit.util.random_selector import RandomSelector
from fpctoolkit.util.path import Path

class Structure(object):
	"""
	Class for representing periodic crystal structures (lattice + basis).

	Holds Lattice instance (2D array) for the lattice and a SiteCollection instance for basis sites.

	For outputting to or inputting from file representations, this class is only compatible with the poscar file type (for now).
	"""

	def __init__(self, file_path=None, lattice=None, sites=None):
		"""
		file_path must be either a valid (relative or absolute) path to a poscar file or None
		lattice must be either a 2D array of floats or ints or a Lattice class instance
		sites must be either a list of sites or a SiteColleciton instance
		"""

		Structure.validate_constructor_arguments(file_path, lattice, sites)

		if file_path:
			self.from_poscar_file_path(file_path)
		else:
			self.lattice = Lattice(lattice)
			self.sites = SiteCollection(sites)


	@staticmethod
	def validate_constructor_arguments(file_path, lattice, sites):

		Path.validate(path=file_path, allow_none=True)

		if not lattice:
			raise Exception("A lattice must be specified.")
		else:
			Lattice.validate_lattice_representation(lattice)

		if not sites:
			raise Exception("A sites list or SiteColleciton instance must be specified.")
		else:
			SiteCollection.validate_sites(sites)


	def __str__(self):
		return str(self.lattice) + "\n".join(str(site) for site in self.sites) + "\n"


	def from_poscar_file_path(self, file_path):

		Path.validate(path=file_path, allow_none=False)
		Path.expand(file_path)

		poscar = Poscar(file_path)
		self.lattice = Lattice(poscar.lattice)
		self.sites = SiteCollection()

		poscar_coordinate_mode = poscar.coordinate_mode
		poscar_coordinates_list = poscar.coordinates

		species_index = 0
		for i, specie in enumerate(poscar.species_list):
			for j in range(poscar.species_count_list[i]):
				new_site = Site()
				new_site['coordinate_mode'] = poscar_coordinate_mode
				new_site['position'] = poscar_coordinates_list[species_index]
				new_site['type'] = specie

				self.sites.append(new_site)

				species_index += 1


	def to_poscar_file_path(self, file_path):
		lattice = self.lattice.to_array()
		species_list = self.sites.get_species_list()
		species_count_list = self.sites.get_species_count_list()
		coordinate_mode = self.sites.get_sorted_list()[0]['coordinate_mode']
		coordinates = self.sites.get_coordinates_list()

		SiteCollection.validate_sites_all_have_same_coordinate_mode(self.sites)

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
		"""
		Takes any site in sites that is in cartesian coordinates and changes
		its position and coordinate mode to be in direct coordinate system
		"""

		for site in self.sites:
			site.convert_to_direct_coordinates(self.lattice)




	def any_sites_are_too_close(self, minimum_atomic_distances_nested_dictionary_by_type, nearest_neighbors_max=3):
		"""
		Returns True if any two sites in this structure are within minimum_atomic_distance (angstroms) of each other.
		Min distances is different for each type pair, as specified by the input dictionary.
		nearest_neighbors_max controls how many nearest neighbor cell images to search.	

		minimum_atomic_distances_nested_dictionary_by_type is in angstroms and looks like:
		{
			'Ba': {'Ba': 1.5, 'Ti': 1.2, 'O': 1.4},
			'Ti': {'Ba': 1.2, 'Ti': 1.3, 'O': 1.3},
			'O':  {'Ba': 1.4, 'Ti': 1.3, 'O': 0.8}
		}
		"""

		sites_list = self.sites.get_sorted_list()

		for site_1_index in range(len(sites_list)):
			for site_2_index in range(site_1_index+1, len(sites_list)):
				site_1 = sites_list[site_1_index]
				site_2 = sites_list[site_2_index]

				minimum_atomic_distance = minimum_atomic_distances_nested_dictionary_by_type[site_1['type']][site_2['type']]

				if self.site_pair_is_too_close(site_1, site_2, minimum_atomic_distance, nearest_neighbors_max):
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

	def get_indices_of_site_pairs_that_are_too_close_to_sites_list(self, site_index_list, minimum_atomic_distances_nested_dictionary_by_type, nearest_neighbors_max=3):
		"""
		Returns list of site pair indices for sites that are within minimum_atomic_distance (angstroms) of each other for any site in sites_list.
		Min distances is different for each type pair, as specified by the input dictionary.
		nearest_neighbors_max controls how many nearest neighbor cell images to search.	

		minimum_atomic_distances_nested_dictionary_by_type is in angstroms and looks like:
		{
			'Ba': {'Ba': 1.5, 'Ti': 1.2, 'O': 1.4},
			'Ti': {'Ba': 1.2, 'Ti': 1.3, 'O': 1.3},
			'O':  {'Ba': 1.4, 'Ti': 1.3, 'O': 0.8}
		}
		"""

		site_pairs_list = []

		pair_hash = {}

		all_sites_list = self.sites.get_sorted_list()

		for site_1_index in site_index_list:
			for site_2_index in range(len(all_sites_list)):
				hash_key = str(site_1_index)+"_"+str(site_2_index)
				hash_key_mirror = str(site_2_index)+"_"+str(site_1_index)

				site_1 = all_sites_list[site_1_index]
				site_2 = all_sites_list[site_2_index]

				if pair_hash.has_key(hash_key) or site_1_index == site_2_index:
					continue

				pair_hash[hash_key] = True
				pair_hash[hash_key_mirror] = True

				minimum_atomic_distance = minimum_atomic_distances_nested_dictionary_by_type[site_1['type']][site_2['type']]

				if self.site_pair_is_too_close(site_1, site_2, minimum_atomic_distance, nearest_neighbors_max):
					site_pairs_list.append([site_1_index, site_2_index])

		return site_pairs_list

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

		for species_type in self.sites.keys():
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

