from collections import OrderedDict
import copy

from fpctoolkit.structure.site import Site

class SiteCollection(object):
	"""Collection of sites

	Tracks ordering and can sort easily.
	Will iterate in order of types added, in blocks of type.

	self.sites is actually an ordered dictionary that looks like:

	sites = {'Ba': [ba_site_1, ba_site_2], 'Ti': [ti_site_1, ...]}



	"""


	def __init__(self, sites_list = []):
		self.sites = OrderedDict()
		self._type_counts = OrderedDict()

		for site in sites_list:
			self.append(site)

	def __iter__(self):
		return iter(self.get_sorted_list())

	def __getitem__(self, index):
		if not isinstance(index, int):
			raise Exception("Site collection index must be an integer")
		else:
			return self.get_sorted_list()[index]

	def __len__(self):
		return len(self.get_sorted_list())

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