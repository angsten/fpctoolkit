from collections import OrderedDict

from fpctoolkit.structure.site_collection import SiteCollection
from fpctoolkit.structure.site_mapping import SiteMapping
from munkres import Munkres

class SiteMappingCollection(object):
	"""
	Finds optimal (net closest) mapping of sites between two site collections
	"""


	def __init__(self, site_collection_initial, site_collection_final, lattice):
		if not SiteCollection.are_commensurate(site_collection_initial, site_collection_final):
			raise Exception("Site collections are not commensurate: they have different types or counts of each type")

		self.site_collection_initial = site_collection_initial
		self.site_collection_final = site_collection_final
		self.lattice = lattice

		self.mapping_dictionary = self.get_site_mapping_dictionary()


	def get_site_mapping_dictionary(self):
		
		munk = Munkres()

		site_mapping_lists_dictionary = OrderedDict() #will look like {'Ba':[site_mapping_1, site_mapping_2, ...], 'Ti':...}

		for type_string in self.site_collection_initial.keys():
			print type_string
			site_mapping_matrix = self.get_site_mapping_matrix(type_string)

			distance_matrix = [[site_mapping.distance for site_mapping in site_mapping_row] for site_mapping_row in site_mapping_matrix]

			print distance_matrix

			mapping_indices = munk.compute(distance_matrix) #looks like [(0, 4), (1, 2), (2, 7), ...] where first in each tuple is row index in site_mapping_matrix
			print mapping_indices

			site_mapping_list = [site_mapping_matrix[i][j] for i, j in mapping_indices]

			site_mapping_lists_dictionary[type_string] = site_mapping_list

		print site_mapping_lists_dictionary
		return site_mapping_lists_dictionary

	def get_site_mapping_matrix(self, type_string):
		"""
		Returns an NxN matrix (where N is number of sites in site_colleciton initial and final) of site_mapping objects for a given species type
		"""

		mapping_matrix = []

		sites_list_initial = self.site_collection_initial[type_string]
		sites_list_final = self.site_collection_final[type_string]

		for initial_site in sites_list_initial:
			mapping_row = []
			for final_site in sites_list_final:
				site_mapping = SiteMapping(initial_site, final_site, self.lattice)
				print site_mapping
				mapping_row.append(site_mapping)

			mapping_matrix.append(mapping_row)

		return mapping_matrix

	def get_average_distance_type_dictionary(self):
		"""
		Returns dict that looks like {'Ba':average_dist_Ba_atoms_from_eachother_in_mapping, 'Ti':...}
		"""
		average_distance_dictionary = OrderedDict()

		for type_string in self.site_collection_initial.keys():
			average_distance = sum([site_mapping.distance for site_mapping in self.mapping_dictionary[type_string]])/len(self.mapping_dictionary[type_string])
			average_distance_dictionary[type_string] = average_distance

		return average_distance_dictionary

	def get_average_displacement_vector_type_dictionary(self):
		"""
		Returns dict that looks like {'Ba':average_direct_coord_vec_Ba_atoms_from_eachother_in_mapping, 'Ti':...}
		"""
		average_displacement_vector_dictionary = OrderedDict()

		for type_string in self.site_collection_initial.keys():
			average_x = sum([site_mapping.displacement_vector[0] for site_mapping in self.mapping_dictionary[type_string]])/len(self.mapping_dictionary[type_string])
			average_y = sum([site_mapping.displacement_vector[1] for site_mapping in self.mapping_dictionary[type_string]])/len(self.mapping_dictionary[type_string])
			average_z = sum([site_mapping.displacement_vector[2] for site_mapping in self.mapping_dictionary[type_string]])/len(self.mapping_dictionary[type_string])
			average_displacement_vector_dictionary[type_string] = [average_x, average_y, average_z]

		return average_displacement_vector_dictionary

	def shift_sites_to_minimize_average_distance(self):
		"""
		Shifts final sites toward initial sites to reduce average displacement vector to zero
		"""

		