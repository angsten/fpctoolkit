



class Site(object):
	"""Sites are generic property sets holding a position in the crystal.

	The properties dictionary holds all properties, including position.
	These can be accessed and set using instance['property_name']

	Example: site = Site()   site['position'] = [0.1, 0.2, 0.0]
	del site['magmom']
	"""

	accepted_keys = ['position', 'type']

	def __init__(self, properties=None):
		if properties:
			self.properties = properties
		else:
			self.properties = {}

	def __nonzero__(self):
		return bool(self.properties)

	def __str__(self):
		return str(self.properties)

	def __getitem__(self, key):
		if key not in self.properties:
			raise Exception("Site does not have property " + str(key))
		else:
			return self.properties[key]

	def __setitem__(self, key, value):
		if key in Site.accepted_keys:
			self.properties[key] = value
		else:
			raise Exception("Key " + str(key) + " is not an accepted site property")

	def __delitem__(self, key):
			del self.properties[key]

	def __contains__(self, key):
		return key in self.properties
