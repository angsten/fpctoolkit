from collections import OrderedDict
import copy

from fpctoolkit.structure.site import Site

class SiteCollection(object):
	"""Collection of sites

	Tracks ordering and can sort easily.
	Will iterate in order of types added, in blocks of type.

	self.sites is actually an ordered dictionary that looks like:

	sites = {'Ba': [Ba_site_1, Ba_site_2], 'Ti': [Ti_site_1, ...]}



	"""


	def __init__(self, sites_list=None):
		self.sites = OrderedDict()
		self._type_counts = OrderedDict()

		if sites_list:
			for site in sites_list:
				self.append(site)

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
		if isinstance(site, Site):
			self.add_site(site)
		else:
			raise Exception("Can only append instances of Site to a site collection")


	def add_site(self, site):
		if site['type'] not in self.sites:
			self.sites[site['type']] = [site]
		else:
			self.sites[site['type']].append(site)

	def remove_site(self, site):
		if site['type'] not in self.sites:
			raise Exception("Site type not present in site collection: " + str(species_type))
		else:
			site['type'].remove(site)

	def get_sorted_list(self):
		"""Returns list of sites for which following is true:
		Makes sure contiguous elements of self.sites of are same type, also
		first type to appear is first type added, second is second type added, ...etc.
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