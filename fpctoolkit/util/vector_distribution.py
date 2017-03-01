



class VectorDistribution(object):
	"""
	Class for generating random vectors following distributions determined by:

	direction_distribution_function: A function that returns a unit vector with some distribution
	magnitude_distribution_function: A function that returns a magnitude with some distribution
	"""


	def __init__(self, direction_distribution_function, magnitude_distribution_function):
		self.direction_distribution_function = direction_distribution_function
		self.magnitude_distribution_function = magnitude_distribution_function

	def get_random_vector(self):
		unit_vector = self.direction_distribution_function()
		magnitude = self.magnitude_distribution_function()

		print magnitude
		print unit_vector

		return unit_vector*magnitude



