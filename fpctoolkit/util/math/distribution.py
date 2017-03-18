#from fpctoolkit.util.math.distribution import Distribution

import numpy as np



class Distribution(object):
	"""
	Custom defined distribution

	Inputs:
	distribution_function: any function f(x) that returns a float - does not have to be normalized in any way - it just describes the relative shape of the distribution.
	min_x: the minimum x value in the domain of the input distribution function f(x)
	max_x: the maximum x vaue in the domain of the input distribution function f(x)

	This class works by approximating the inverse cumulative distribution function with a list of length point_count.
	The main function, get_random_value, returns a value in range [min_x, max_x) with relative frequencies determined by the 
	probability distribution function, f(x).
	"""

	point_count = 50000

	def __init__(self, distribution_function, min_x, max_x):
		


		self.distribution_function = distribution_function
		self.min_x = min_x
		self.max_x = max_x

		self.tick_width = (max_x - min_x)/Distribution.point_count

		self.cumulative_function = []
		self.calculate_cumulative_function()
		self.normalize_cumulative_function()

		self.inverse_cumulative_function = []
		self.calculate_inverse_cumulative_function()

	def calculate_cumulative_function(self):

		total = 0.0
		for i in range(0, Distribution.point_count):

			x_value = self.get_x_value_from_index(i)

			probability = self.distribution_function(x_value)

			if probability < 0.0:
				raise Exception("Cannot have a negative probability")

			total += probability

			self.cumulative_function.append(total)

	def normalize_cumulative_function(self):
		normalizing_ratio = 1.0/self.cumulative_function[-1]
		self.cumulative_function = [value*normalizing_ratio for value in self.cumulative_function]

	def calculate_inverse_cumulative_function(self):

		cumulative_probability_counter = 0.0
		for i in range(len(self.cumulative_function)):
			current_cumulative_probability = self.cumulative_function[i]

			while cumulative_probability_counter < current_cumulative_probability:
				self.inverse_cumulative_function.append(self.get_x_value_from_index(i))

				cumulative_probability_counter += (1.0/Distribution.point_count)



	def get_x_value_from_index(self, index):
		return self.min_x + index*self.tick_width

	def get_index_from_x_value(self, x_value):
		x_difference = x_value - self.min_x

		return x_difference/self.tick_width

	def get_index_from_cumulative_probability(self, cumulative_probability):
		return int(cumulative_probability*Distribution.point_count)



	def get_random_value(self):
		"""
		Returns a random floating point number that follows the distribution
		"""

		cumulative_probability = np.random.random() #y value of cumulative distribution


		#convert cumulative_probability to be one of ticks
		inverse_cumulative_index = self.get_index_from_cumulative_probability(cumulative_probability)

		return self.inverse_cumulative_function[inverse_cumulative_index] #get corresponding x value