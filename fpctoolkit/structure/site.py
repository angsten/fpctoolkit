import numpy as np

from fpctoolkit.util.vector import Vector

class Site(object):
	"""Sites are generic property sets holding a position in the crystal.

	The properties dictionary holds all properties, including position.
	These can be accessed and set using instance['property_name']

	Example: site = Site()   site['position'] = [0.1, 0.2, 0.0]
	site['type'] = 'Ba'
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

	def displace(self, vector):
		"""Displaces site's position by vector - no knowledge of
		coordinate mode.
		"""

		for i in range(3):
			self._properties['position'][i] += vector[i]


	@staticmethod
	def get_coordinate_mode_string(coord_sys_line):
		if 'D' in coord_sys_line.upper():
			return 'Direct'
		elif 'C' in coord_sys_line.upper():
			return 'Cartesian'
		else:
			raise Exception("Coordinate system type not valid for site: " + coord_sys_line)