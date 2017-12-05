#from fpctoolkit.structure.structure_analyzer import StructureAnalyzer

import copy

from fpctoolkit.structure.structure import Structure
from fpctoolkit.util.math.vector import Vector


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



	@staticmethod
	def get_force_potential_samples(structure, N_max=1, cutoff_fraction=0.9):
		"""
		Returns a list of lists, where each sample looks like [[fx of atom 1, fy, fz, x_dist_to_1st_closest_atom (cartesian), y_dist_to...], [fx of atom 2, fy, fz, ...], ...]
		"""

		structure.convert_sites_to_direct_coordinates()

		distance_cutoff = max(max(structure.lattice[0]), max(structure.lattice[1]), max(structure.lattice[2]))*cutoff_fraction


		all_positions = []

		for x in range(-N_max, N_max+1):
			for y in range(-N_max, N_max+1):
				for z in range(-N_max, N_max+1):

					for site in structure.sites:

						all_positions.append([site['position'][0]+x, site['position'][1]+y, site['position'][2]+z])


		structure.convert_sites_to_cartesian_coordinates()

		for i in range(len(all_positions)):
			all_positions[i] = Vector.get_in_cartesian_coordinates(direct_vector=all_positions[i], lattice=structure.lattice)


		samples = []

		for i, site in enumerate(structure.sites):

			#print "Calculating sample for site: ", i

			site_position = site['position']

			sample = copy.deepcopy(site['force'])

			dist_pos_duples_list = []

			for j in range(len(all_positions)):

				other_position = all_positions[j]

				difference_vector = [(other_position[r]-site_position[r]) for r in range(3)]

				distance = (difference_vector[0]**2.0 + difference_vector[1]**2.0 + difference_vector[2]**2.0)**0.5

				if distance < 0.00001:
					continue
				elif distance > distance_cutoff:
					continue

				dist_pos_duples_list.append([distance, difference_vector])


			dist_pos_duples_list = sorted(dist_pos_duples_list, key=lambda x: x[0])

			for z in range(len(dist_pos_duples_list)):
				sample += dist_pos_duples_list[z][1]


			samples.append(sample)

		
		sample_lengths = [len(s) for s in samples]

		min_length = min(sample_lengths)

		for sample in samples:
			sample = sample[0:min_length]

		return samples