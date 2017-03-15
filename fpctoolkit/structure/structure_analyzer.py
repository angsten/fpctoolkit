#from fpctoolkit.structure.structure_analyzer import StructureAnalyzer


from fpctoolkit.structure.structure import Structure
from fpctoolkit.util.vector import Vector


class StructureAnalyzer(object):
	"""
	Defines static methods useful for analyzing Structure instances. No functions modify the structure being analyzed.
	"""

	@staticmethod
	def any_sites_are_too_close(structure, minimum_atomic_distances_nested_dictionary_by_type, nearest_neighbors_max=3):
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

		Structure.validate(structure)

		sites_list = structure.sites.get_sorted_list()

		for site_1_index in range(len(sites_list)):
			for site_2_index in range(site_1_index+1, len(sites_list)):
				site_1 = sites_list[site_1_index]
				site_2 = sites_list[site_2_index]

				minimum_atomic_distance = minimum_atomic_distances_nested_dictionary_by_type[site_1['type']][site_2['type']]

				if StructureAnalyzer.site_pair_is_too_close(structure, site_1, site_2, minimum_atomic_distance, nearest_neighbors_max):
					return True

		return False

	@staticmethod
	def site_pair_is_too_close(structure, site_1, site_2, minimum_atomic_distance, nearest_neighbors_max=3):
		"""
		Returns true if site_1 position is within minimum_atomic_distance of site_2 position under periodic boundary conditions.
		nearest_neighbors_max controls how many nearest neighbor cell images to search. Higher means higher accuracy in heavily sheared structures
		"""

		site_1.convert_to_direct_coordinates(structure.lattice)
		site_2.convert_to_direct_coordinates(structure.lattice)

		distance = Vector.get_minimum_distance_between_two_periodic_points(site_1['position'], site_2['position'], structure.lattice, nearest_neighbors_max)

		return (distance < minimum_atomic_distance)

	@staticmethod
	def get_indices_of_site_pairs_that_are_too_close_to_sites_list(structure, site_index_list, minimum_atomic_distances_nested_dictionary_by_type, nearest_neighbors_max=3):
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

		all_sites_list = structure.sites.get_sorted_list()

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

				if StructureAnalyzer.site_pair_is_too_close(structure, site_1, site_2, minimum_atomic_distance, nearest_neighbors_max):
					site_pairs_list.append([site_1_index, site_2_index])

		return site_pairs_list

	@staticmethod
	def any_sites_are_too_close_to_site(structure, test_site, minimum_atomic_distances_nested_dictionary_by_type, nearest_neighbors_max=3):
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

		####################not implemented yet!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

		for species_type in structure.sites.keys():
			if species_type not in minimum_atomic_distances_nested_dictionary_by_type:
				raise Exception("Minimum atomic for all pairs of types in this structure not specified.")

		structure.convert_sites_to_direct_coordinates()

		test_site_fractional_coordinates = test_site['position'] if test_site['coordinate_mode'] == 'Direct' else Vector.get_in_direct_coordinates(test_site['position'], structure.lattice)

		for other_site in structure.sites:
			if test_site is other_site: #don't consider case where these are the same site objects
				continue

			minimum_distance = Vector.get_minimum_distance_between_two_periodic_points(test_site_fractional_coordinates, other_site['position'], self.lattice, nearest_neighbors_max)
			minimum_atomic_distance = minimum_atomic_distances_nested_dictionary_by_type[test_site['type']][other_site['type']]

			if minimum_distance < minimum_atomic_distance:
				return True

		return False