from collections import OrderedDict
import copy

from fpctoolkit.structure.site import Site

class SiteCollection(object):
	"""
	Collection of Site objects.

	self.sites is an ordered dictionary that looks like:   {'Ba': [Ba_site_1, Ba_site_2], 'Ti': [Ti_site_1, ...]}


	sites['Ba'] will return a list of all sites where site['type'] is 'Ba'. This list will retain
	the original order of insertion.

	site_collection.get_sorted_list() returns a single list of all sites, arranged in subgroups of type (by order of type insertion), with each
	subgroup retaining its original insertion order.

	An iterator on a SiteCollection will iterate through elements of site_collection.get_sorted_list()
	"""


	def __init__(self, sites=None):
		"""
		sites must be either None, a list of Site instances, or a SiteCollection instance.
		"""

		SiteCollection.validate_constuctor_arguments(sites)

		self.sites = OrderedDict()

		if sites:
			for site in sites:
				self.append(site)

	@staticmethod
	def validate_constuctor_arguments(sites):
		SiteCollection.validate_sites(sites)

	@staticmethod
	def validate_sites(sites):
		"""
		sites must be either a list of instances of the Site class or a SiteCollection instance.
		"""

		if isinstance(sites, list) or isinstance(sites, SiteCollection):
			for site in sites:
				Site.validate_site(site)
		else:
			raise Exception("sites must be either a list of Site instances or a SiteColleciton instance")


	def __iter__(self):
		return iter(self.get_sorted_list())

	def __getitem__(self, key):
		if isinstance(key, basestring): #access by type like 'Ba'
			if key in self.sites:
				return self.sites[key]
			else:
				return []
		elif isinstance(key, int):
			return self.get_sorted_list()[key]
		else:
			raise Exception("Site collection key must be an integer or string")
		

	def __len__(self):
		return len(self.get_sorted_list())

	def keys(self):
		return self.sites.keys()

	def __contains__(self, key):
		return key in self.sites

	def append(self, site):
		Site.validate_site(site)
		self.add_site(site)


	def add_site(self, site):
		if site['type'] not in self.sites:
			self.sites[site['type']] = [site]
		else:
			self.sites[site['type']].append(site)

	def remove_site(self, site):
		site_type = site['type']

		if site_type not in self.sites:
			raise Exception("Site type not present in site collection: " + str(site_type))
		else:
			self.sites[site_type].remove(site)

			if len(self.sites[site_type]) == 0: #this type no longer appears in the collection - remove the dictionary key for this type in sites.
				del sites[site_type]

	def get_sorted_list(self):
		"""
		Returns list of sites for which following is true:
			Contiguous elements of self.sites of are of the same type
			The first type to appear is the first type that was added, second is second type added, ...etc.
		"""

		sorted_list = []

		for species_type, species_site_list in self.sites.items():
			sorted_list += species_site_list

		return sorted_list

	def get_species_list(self):
		return self.sites.keys()

	def get_species_count_list(self):
		return [len(self.sites[species_type]) for species_type in self.sites]

	def get_coordinates_list(self):
		return [site['position'] for site in self]

	def shift_direct_coordinates(self, direct_displacement_vector, reverse=False):
		if reverse:
			for j in range(3):
				direct_displacement_vector[j] = -direct_displacement_vector[j]

		for site in self:
			site.displace(direct_displacement_vector)

	def shift_direct_coordinates_by_type(self, shift_vector_dictionary, reverse=False):
		"""
		Shifts all sites of type 'type' in collection by shift_vector_dictionary['type'] or -shift_vector_dictionary['type'] if reverse is true
		"""

		if len(self.keys()) != len(shift_vector_dictionary.keys()):
			raise Exception("Shift vector dictionary is not commensurate with sites")

		for type_string in shift_vector_dictionary.keys():
			for i, site in enumerate(self[type_string]):
				site = self[type_string][i]

				if not (site['coordinate_mode'] == 'Direct'):
					raise Exception("Site not in direct coordinate mode - cannot shift")
				else:
					for j in range(3):
						if reverse:
							site['position'][j] += -shift_vector_dictionary[type_string][j]
						else:
							site['position'][j] += shift_vector_dictionary[type_string][j]


	@staticmethod
	def are_commensurate(site_collection_1, site_collection_2):
		"""
		Returns true if same types of sites and same number of each site in each collection
		"""

		for key in site_collection_1.keys():
			if not key in site_collection_2.keys():
				return False
			else:
				if len(site_collection_1[key]) != len(site_collection_2[key]):
					return False

		return True