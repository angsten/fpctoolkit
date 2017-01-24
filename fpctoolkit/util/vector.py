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
