

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

		self.mapping_dictionary = self.get_site_mapping_index_dictionary()


	def get_site_mapping_index_dictionary(self):
		
		munk = Munkres()

		site_mapping_index_dictionary = {} #will look like {'Ba':[site_mapping_1, site_mapping_2, ...], 'Ti':...}

		for type_string in self.site_collection_initial.keys():
			print type_string
			site_mapping_matrix = self.get_site_mapping_matrix(type_string)

			distance_matrix = [[site_mapping.distance for site_mapping in site_mapping_row] for site_mapping_row in site_mapping_matrix]

			print distance_matrix

			mapping_indices = munk.compute(distance_matrix) #looks like [(0, 4), (1, 2), (2, 7), ...] where first in each tuple is row index in site_mapping_matrix
			print mapping_indices

			site_mapping_list = [site_mapping_matrix[i][j] for i, j in mapping_indices]

			site_mapping_index_dictionary[type_string] = site_mapping_list




		return site_mapping_index_dictionary

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