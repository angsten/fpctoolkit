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
		return " ".join(str(component) for component in self.to_list())

	def to_list(self):
		return [self.x, self.y, self.z]

	@property
	def magnitude(self):
		return (self.x**2.0 + self.y**2.0 + self.z**2.0)**0.5

	@staticmethod
	def get_in_cartesian_coordinates(direct_vector, lattice):
		"""Returns vector with coordinates transformed to
		the equivalent cartesian coordinate representation.
		No clipping is performed to keep in unit cell.
		"""

		x = direct_vector[0]*lattice[0][0] + direct_vector[1]*lattice[1][0] + direct_vector[2]*lattice[2][0]
		y = direct_vector[0]*lattice[0][1] + direct_vector[1]*lattice[1][1] + direct_vector[2]*lattice[2][1]
		z = direct_vector[0]*lattice[0][2] + direct_vector[1]*lattice[1][2] + direct_vector[2]*lattice[2][2]

		return Vector([x,y,z])


	@staticmethod
	def get_in_direct_coordinates(cartesian_vector, lattice):
		"""Returns vector with coordinates transformed to
		the equivalent direct coordinate representation.
		No clipping is performed to keep in unit cell.
		"""
		a = lattice[0]
		b = lattice[1]
		c = lattice[2]

		A = np.array([[a[0], b[0], c[0]], [a[1], b[1], c[1]], [a[2], b[2], c[2]]])
		X = np.array([cartesian_vector[0], cartesian_vector[1], cartesian_vector[2]])

		A_inverse = np.linalg.inv(A)
		d = np.dot(A_inverse, X)

		return Vector([d[0], d[1], d[2]])


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
		"""
		returns a vector with random direction and magnitude
		governed by normal distribution. No absolute value
		is taken on the magnitude - can be negative or positive.
		"""
		direction = Vector.get_random_unit_vector()

		if magnitude_stdev == 0.0:
			magnitude = magnitude_average
		else:
			magnitude = np.random.normal(magnitude_average, magnitude_stdev)

		return direction*magnitude

	@staticmethod
	def normalize_fractional_coordinate(coordinate):
		"""Puts each component of coordinate in range [0.0 and 1.0)"""
		for i in range(3):
			while coordinate[i] >= 1.0:
				coordinate[i] -= 1.0
			while coordinate[i] < 0.0:
				coordinate[i] += 1.0

	@staticmethod
	def put_fractional_coordinate_nearest_to_origin(coordinate):
		"""Puts all components in range (-0.5, 0.5]"""

		for i in range(3):
			while coordinate[i] > 0.5:
				coordinate[i] -= 1.0
			while coordinate[i] <= -0.5:
				coordinate[i] += 1.0

	@staticmethod
	def get_minimum_distance_between_two_periodic_points(fractional_coordinate_1, fractional_coordinate_2, lattice, N_max=3, return_vector=False):
		"""
		Given periodic boundary conditions specified by lattice and positions 1 and 2 in 
		fractional coordinates, return the shorted distance between these two points

		N_max controls how many images out to search - in general, need a higher N max for lattices with larger a*c b*c and a*b dot products
		Scales (2.0*N_max)^3 in computing time though!

		If return_vector, (min_dist_float, min_dist_vector_in_direct_coords) tuple is returned
		"""

		#first, normalize fractional coordinate components to be within 0.0 and 1.0
		Vector.normalize_fractional_coordinate(fractional_coordinate_1)
		Vector.normalize_fractional_coordinate(fractional_coordinate_2)

		#Now, both coordinates are contained within the same cell

		d = np.array([fractional_coordinate_2[0] - fractional_coordinate_1[0], fractional_coordinate_2[1] - fractional_coordinate_1[1], fractional_coordinate_2[2] - fractional_coordinate_1[2]])

		# print "Original d: ", d

		Vector.put_fractional_coordinate_nearest_to_origin(d) #Want to center the relative distance vector

		# print "Shifted d: ", d

		a = np.array(lattice[0])
		b = np.array(lattice[1])
		c = np.array(lattice[2])

		A = np.dot(a, a)
		B = np.dot(b, b)
		C = np.dot(c, c)

		D = 2*np.dot(a, b)
		E = 2*np.dot(a, c)
		F = 2*np.dot(b, c)

		#This gives magnitude squared of distance vector as a function of fractional coordinates (fa, fb, fc)
		def G(fa, fb, fc): return A*fa**2 + B*fb**2 + C*fc**2 + D*fa*fb + E*fa*fc + F*fb*fc

		fa = d[0]
		fb = d[1]
		fc = d[2]

		minimum_distance_squared = G(fa - N_max, fb - N_max, fc - N_max)
		minimum_distance_vector_in_direct_coordinates = [fa - N_max, fb - N_max, fc - N_max]
		#min_set = [N_max]*3

		for Na in range(-N_max, N_max + 1):
			for Nb in range(-N_max, N_max + 1):
				for Nc in range(-N_max, N_max + 1):
					distance_squared = G(fa - Na, fb - Nb, fc - Nc)

					if distance_squared < minimum_distance_squared:
						minimum_distance_squared = distance_squared
						minimum_distance_vector_in_direct_coordinates = [fa - Na, fb - Nb, fc - Nc]
						#min_set = [Na, Nb, Nc]



		#print A, B, C, D, E, F
		#print "Min set ", min_set

		if return_vector:
			return (minimum_distance_squared**0.5, minimum_distance_vector_in_direct_coordinates)
		else:
			return minimum_distance_squared**0.5



