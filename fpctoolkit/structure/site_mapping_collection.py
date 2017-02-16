

from fpctoolkit.structure.site_collection import SiteCollection
from fpctoolkit.structure.site_mapping import SiteMapping

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

		



