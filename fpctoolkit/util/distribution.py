import numpy as np



class Distribution(object):
	"""
	Custom defined distribution
	"""

	point_count = 5000

	def __init__(self, distribution_function, min_x, max_x):
		


		self.distribution_function = distribution_function
		self.min_x = min_x
		self.max_x = max_x

		self.tick_width = (max_x - min_x)/Distribution.point_count

		self.cumulative_function = []
		self.calculate_cumulative_function()
		self.normalize_cumulative_function()

	def calculate_cumulative_function():

		total = 0.0
		for i in range(0, Distribution.point_count):
			x_value = self.get_x_value_from_index(i)

			total += self.distribution_function(x_value)

			self.cumulative_function.append(total)

	def normalize_cumulative_function():
		normalizing_ratio = 1.0/self.cumulative_function[-1]
		self.cumulative_function = [value*normalizing_ratio for value in self.cumulative_function]

	def calculate_inverse_cumulative_function():

		for i in range(len(self.cumulative_function)):


	def get_x_value_from_index(self, index):
		return self.min_x + index*self.tick_width

	def get_index_from_x_value(self, x_value):
		x_difference = x_value - self.min_x

		return x_difference/self.tick_width



	def get_random_value():
		"""
		Returns a random floating point number that follows the distribution
		"""

		probability = np.random.random()