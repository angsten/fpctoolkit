import numpy as np



class Vector(object):

	def __init__(self, components_list):
		if len(components_list) != 3:
			raise Exception("Vector components list argument must list of floats of length three")

		self.x = components_list[0]
		self.y = components_list[1]
		self.z = components_list[2]

	def __getitem__(self, key):
		if not isinstance(key, int):
			raise Exception("Key must be index between 0 and 2 of type int")

		if key == 0:
			return self.x
		elif key ==1:
			return self.y
		elif key ==2:
			return self.z

	def __mul__(self, value):
		if isinstance(value, list) or isinstance(value, tuple) or isinstance(value, Vector):
			return Vector([self[i]*value[i] for i in range(3)])
		elif isinstance(value, float) or isinstance(value, int):
			return Vector([self[i]*value for i in range(3)])
		else:
			raise Exception("Cannot multiply vector by this type")

	__rmul__ = __mul__

	def __str__(self):
		return " ".join(str(component) for component in [self.x, self.y, self.z])

	@property
	def magnitude(self):
		return (self.x**2.0 + self.y**2.0 + self.z**2.0)**0.5

	@staticmethod
	def get_in_direct_coordinates(self, vector, lattice):
		"""Returns vector with coordinates transformed to
		the equivalent direct coordinate representation.
		No clipping is performed to keep in unit cell.
		"""

	@staticmethod
	def get_random_unit_vector():
	    """
	    Get a random 3D unit vector with uniform spherical distribution
	    """
	    phi = np.random.uniform(0.0, np.pi*2.0)
	    cosoftheta = np.random.uniform(-1.0, 1.0)
	    theta = np.arccos(cosoftheta)

	    x = np.sin(theta) * np.cos(phi)
	    y = np.sin(theta) * np.sin(phi)
	    z = np.cos(theta)

	    return Vector([x,y,z])

	@staticmethod
	def get_random_vector(magnitude_average, magnitude_stdev):
		"""returns vector with random direction and magnitude
		governed by normal distribution. No absolute value
		is taken on the magnitude - can be negative or positive.
		"""
		direction = Vector.get_random_unit_vector()

		if magnitude_stdev == 0.0:
			magnitude = magnitude_average
		else:
			magnitude = np.random.normal(magnitude_average, magnitude_stdev)

		return direction*magnitude
