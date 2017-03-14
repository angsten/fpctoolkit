from collections import OrderedDict
import copy

from fpctoolkit.structure.site import Site
from fpctoolkit.util.vector import Vector

class SiteCollection(object):
	"""
	Collection of Site objects. The objects are validated to at minimum have a position, coordinate mode, and type.

	self.sites is an ordered dictionary that looks like:   {'Ba': [Ba_site_1, Ba_site_2], 'Ti': [Ti_site_1, ...]}


	sites['Ba'] will return a list of all sites where site['type'] is 'Ba'. This list will retain the original order of insertion.

	sites[1] will give sites.get_sorted_list()[1]

	len(sites) will return length of sites in collection

	sites.keys() returns a list of all site sypes present in the colleciton (['Ba', 'Ti'])

	sites.append(Site(...)) will add the given Site instance to the site colleciotn.

	sites.remove(Site) will remove the (address equivalent) site in the collection.

	site_collection.get_sorted_list() returns a list of all sites grouped by type. The order in which blocks of types appear is determined
	by type insertion order. Within type blocks, sites are ordered by insertion order.

	An iterator on a SiteCollection will iterate through elements of site_collection.get_sorted_list()
	"""


	def __init__(self, sites=None):
		"""
		sites must be either None, a list of Site instances, or a SiteCollection instance.

		Only shallow copies are made of the input sites.
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
			raise Exception("sites must be either a list of Site instances or a SiteColleciton instance. Type is", type(sites))


	def __iter__(self):
		return iter(self.get_sorted_list())

	def __getitem__(self, key):
		if isinstance(key, basestring): #access by type, like site_collection['Ba']
			if key in self.sites:
				return self.sites[key]
			else:
				raise Exception("Species type", key, "does not exist in SiteCollection instance.")

		elif isinstance(key, int):
			sites_list = self.get_sorted_list()

			if key < 0 or key >= len(sites_list):
				raise IndexError
			else:
				return sites_list[key]
		else:
			raise Exception("Site collection key must be an integer or string. Key given is", key)
		

	def __len__(self):
		"""
		Returns the total number of sites in the collection.
		"""

		return len(self.get_sorted_list())

	def keys(self):
		"""
		Returns list of all keys of self.sites (like ['Ba', 'Ti'])
		"""

		return self.sites.keys()

	def __contains__(self, key):
		if not isinstance(key, basestring):
			raise Exception("SiteCollection instance cannot contain non-string key:", key)

		return key in self.sites


	def append(self, site):
		"""
		Appends a shallow copy of site to self.sites.
		"""

		Site.validate_site(site)

		site_type = site['type']

		if site_type not in self.sites:
			self.sites[site_type] = [site] #start a new list for this specie
		else:
			self.sites[site_type].append(site) #add to an existing list of these species


	def remove(self, site):
		Site.validate_site(site)

		site_type = site['type']

		if site_type not in self.sites:
			raise Exception("Site type not present in site collection:", str(site_type))
		else:
			self.sites[site_type].remove(site)

			if len(self.sites[site_type]) == 0: #this type no longer appears in the collection - remove the dictionary key for this type in sites.
				del sites[site_type]

	def get_sorted_list(self):
		"""
		Returns a list of Site instances for which following is true:
			Contiguous elements of the list of are of the same type
			The first type to appear in the list is the first type that was added, second is second type added, ...etc.
		"""

		sorted_list = []

		for species_type, species_site_list in self.sites.items():
			sorted_list += species_site_list

		return sorted_list


	def get_species_list(self):
		"""
		Returns list of types like: ['Ba', 'Ti', 'O']
		"""
		return self.sites.keys()

	def get_species_count_list(self):
		"""
		Returns list of counts of each type in the collection like [1, 1, 3]
		"""

		return [len(self.sites[species_type]) for species_type in self.sites]

	def get_coordinates_list(self):
		"""
		Returns a list of 3D vectors representing the coordinates of each site. This list is sorted by type and site insertion.
		"""

		return [site['position'] for site in self.get_sorted_list()]




	###################################################################################################################

	def shift_direct_coordinates(self, direct_displacement_vector, reverse=False):
		"""
		Shifts all sites by the 3D vector (expressed in direct coordinates) direct_displacement_vector.
		Errors if not all sites in the collection are in direct coordinates already.

		If reverse is True, sites are shifted by -direct_displacement_vector
		"""

		Vector.validate_3D_vector_representation(direct_displacement_vector)

		if reverse:
			for j in range(3):
				direct_displacement_vector[j] = -direct_displacement_vector[j]

		for site in self:
			if not (site['coordinate_mode'] == 'Direct'):
				raise Exception("Site not in direct coordinate mode: cannot shift all sites in this SiteCollection.")

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
		Returns True if the two site collections hold the same set of site types and the same number of each site in each type.
		"""

		for key in site_collection_1.keys():
			if not (key in site_collection_2.keys()):
				return False
			else:
				if len(site_collection_1[key]) != len(site_collection_2[key]):
					return False

		return True