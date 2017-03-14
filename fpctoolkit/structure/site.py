#from fpctoolkit.structure.site import Site

import numpy as np

from fpctoolkit.util.vector import Vector


class Site(object):
	"""
	Sites are generic property sets which have a (periodic) position in the crystal.

	A properties dictionary self._properties holds all properties, including position.
	These can be accessed and set using instance['property_name']

	Example: 
	site = Site()   
	site['position'] = [0.1, 0.2, 0.0]
	site['type'] = 'Ba' (it's a good idea to keep this as element names always)
	site['coordinate_mode'] = 'Cartesian'
	del site['magmom']

	can also do: site['position'] = [0.1, 0.2, 0.0, 'cart']
	"""

	accepted_keys = ['position', 'coordinate_mode', 'type']

	def __init__(self, properties=None):
		self._properties = {}

		if properties: #safeley add given properties
			for key, value in properties.items():
				self[key] = value

	def __nonzero__(self):
		return bool(self._properties)

	def __str__(self):
		return str(self._properties)

	def __getitem__(self, key):
		if key not in self._properties:
			raise Exception("Site does not have property " + str(key))
		else:
			return self._properties[key]

	def __setitem__(self, key, value):
		if key in Site.accepted_keys:
			if key == 'position':
				if len(value) == 4: #has coord mode string at end [0.1, 0.1, 0.2, 'cart']
					self._properties['coordinate_mode'] = Site.get_coordinate_mode_string(value[3])
					value.pop()
				if not len(value) == 3:
					raise Exception("Site positions must have three components")
			elif key == 'coordinate_mode':
				value = Site.get_coordinate_mode_string(value)
			elif key == 'type':
				if not isinstance(value, basestring):
					raise Exception("Type must be of type string")

			self._properties[key] = value
		else:
			raise Exception("Key " + str(key) + " is not an accepted site property")

	def __delitem__(self, key):
			del self._properties[key]

	def __contains__(self, key):
		return key in self._properties


	def get_properties_dictionary(self):
		return self._properties

	def convert_to_cartesian_coordinates(self, lattice):
		"""
		Takes site in direct coordinates and changes
		its position and coordinate mode to be in cartesian coordinate system
		"""

		if self['coordinate_mode'] == 'Direct':
			self['coordinate_mode'] = 'Cartesian'
			self['position'] = Vector.get_in_cartesian_coordinates(self['position'], lattice).to_list()

	def convert_to_direct_coordinates(self, lattice):
		"""
		Takes site in cartesian coordinates and changes
		its position and coordinate mode to be in direct coordinate system
		"""

		if self['coordinate_mode'] == 'Cartesian':
			self['coordinate_mode'] = 'Direct'
			self['position'] = Vector.get_in_direct_coordinates(self['position'], lattice).to_list()

	def displace(self, vector):
		"""
		Displaces site's position by vector with no knowledge of what the current coordinate mode.
		"""

		Vector.validate_3D_vector_representation(vector)

		for i in range(3):
			self._properties['position'][i] += vector[i]

	def randomly_displace(self, displacement_vector_distribution_function_dictionary_by_type, lattice):

		displacement_vector = displacement_vector_distribution_function_dictionary_by_type[self['type']]()

		if self['coordinate_mode'] == 'Direct':
			displacement_vector = Vector.get_in_direct_coordinates(displacement_vector, lattice)

			self.displace(displacement_vector)

	@staticmethod
	def get_coordinate_mode_string(coord_sys_line):
		if 'D' in coord_sys_line.upper():
			return 'Direct'
		elif 'C' in coord_sys_line.upper():
			return 'Cartesian'
		else:
			raise Exception("Coordinate system type not valid for site: " + coord_sys_line)

	@staticmethod
	def sites_are_equal(site_1, site_2): ##############improve this!!!
		if site_1['type'] != site_2['type']:
			return False

		for component in range(3):
			if (site_1['position'][component] - site_2['position'][component]) > 0.0000000001:
				return False

	@staticmethod
	def validate_site(site):
		"""
		Raises an exception if site is not a valid representaiton of a site and does not at least contain a position, coordinate_mode, and a type property.
		"""

		if not isinstance(site, Site):
			raise Exception("Site is not of type Site. Type is ", type(site))

		if site.has_key('position') and site.has_key('coordinate_mode'):
			Vector.validate_3D_vector_representation(site['position'])
		else:
			raise Exception("A valid site must define a position and coordinate mode. Site is:", site)


		if not (site.has_key('type') and isinstance(site['type'], basestring)):
			raise Exception("A valid site must define a type, and this must be a string. Site is:", site)