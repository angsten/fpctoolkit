#from fpctoolkit.util.math.distribution import Distribution

import numpy as np

import fpctoolkit.util.basic_validators as basic_validators


class Distribution(object):
	"""
	Custom defined probability distribution. A distribution can have any shape but is normalized (integral over all possible values is one).

	To get output from the Distribution class, call dist.get_random_value(). The values thus produced will have the relative frequency given by shape_function and will be within
	the values of min_x and max_x. It's equivalent to an observation of a random variable with a provided distribution.

	Example usage:
	dist = Distribution(shape_function=lambda x: x**2, min_x=10, max_x=20)
	magnitude = dist.get_random_value() #output will be from 10 to 20, with 20 having a 40X chance compared to 10

	This class works by approximating the inverse cumulative distribution function with a list of length tick_count.
	The main function, get_random_value, returns a value in range [min_x, max_x) with relative frequencies determined by the 
	probability distribution function, f(x).
	"""

	def __init__(self, shape_function, min_x, max_x, tick_count=10000):
		"""
		shape_function: any function f(x) that returns a real number for x in [min_x, max_x]. The shape function does not have to be normalized in any way - it just describes the relative shape of the distribution.
		f(x) only has to be a valid real-number-returning function from min_x to max_x inclusive.

		min_x: the minimum x value in the domain of the input shape function f(x).

		max_x: the maximum x vaue in the domain of the input shape function f(x). Can be equal to min_x (in which case min_x is always returned in dist.get_random_value())

		tick_count: how many elements in the approximation arrays. Higher number means slower performance but higher accuracy.
		"""
		
		basic_validators.validate_first_real_number_is_strictly_less_than_or_equal_to_second(min_x, max_x)
		Distribution.validate_shape_function(shape_function, min_x, max_x)
		basic_validators.validate_positive_nonzero_integer(tick_count)

		min_x = float(min_x)
		max_x = float(max_x)

		self.shape_function = shape_function
		self.min_x = min_x
		self.max_x = max_x
		self.tick_count = tick_count

		self.tick_width = (max_x - min_x)/tick_count

		self.cumulative_function = []
		self.calculate_cumulative_function()
		self.normalize_cumulative_function()

		self.inverse_cumulative_function = []
		self.calculate_inverse_cumulative_function()

	@staticmethod
	def validate_shape_function(shape_function, min_x, max_x):
		"""
		Raises an exception if the shape function errors over the given range or if it produces anything other than real numbers that are positive or zero.
		"""

		shape_function_outputs = []

		try:
			shape_function_outputs.append(shape_function(min_x))
			shape_function_outputs.append(shape_function(max_x))

			for i in range(40):
				shape_function_outputs.append(shape_function(np.random.uniform(min_x, max_x)))

		except Exception as exception_instance:
			raise Exception("Shape function fails for some numbers in the range min_x to max_x. Exception raised when calling the shape function is: ", exception_instance)


		for shape_function_output in shape_function_outputs:
			basic_validators.validate_real_number_is_positive_or_zero(shape_function_output)


	@staticmethod
	def validate_distribution(distribution):
		"""
		Raises an exception if distribution is either not an instance of Distribution, or if the get_random_value() function does not work as expected.
		"""

		if not isinstance(distribution, Distribution):
			raise Exception("Type must be Distribution. Type is", type(distribution))

		try:
			distribution.get_random_value()
		except Exception as exception_instance:
			raise Exception("Distribution instance failedto generate a random value. Exception raised when calling get_random_value() is: ", exception_instance)



	def calculate_cumulative_function(self):
		"""
		Calculates a cumulative distribution function based on the shape function and represents in an approximate array form. As shape function is not normalized, 
		so will the CDF not yet be normalized at the end of this method.
		"""

		total = 0.0
		for i in range(0, self.tick_count):

			x_value = self.get_x_value_from_index(i)

			probability = self.shape_function(x_value)

			basic_validators.validate_real_number_is_positive_or_zero(probability)

			total += probability

			self.cumulative_function.append(total)

	def get_x_value_from_index(self, index):
		"""
		Returns the x value input to the distribution function that corresponds to the given array index of the approximation lists.
		"""

		basic_validators.validate_sequence_index(index, self.tick_count)

		x_value = self.min_x + index*self.tick_width

		basic_validators.validate_real_number_is_in_range(x_value, self.min_x, self.max_x)

		return x_value

	def normalize_cumulative_function(self):
		"""
		Normalize the cumulative distribution function array approximation such that the last value in the array is 1.0.
		"""

		total_accumulation_value = self.cumulative_function[-1]

		if total_accumulation_value <= 0.0:
			raise Exception("Input distribution shape function gave way to a cumulative distribution that is zero or negative at max_x.")

		normalizing_ratio = 1.0/total_accumulation_value

		self.cumulative_function = [value*normalizing_ratio for value in self.cumulative_function]

	def calculate_inverse_cumulative_function(self):
		"""
		Construct an approximation array to the inverse cumulative function. This maps the x value of a random variable to a CDF(x) value (0.0 to 1.0)
		"""

		cumulative_probability_counter = 0.0
		for i in range(len(self.cumulative_function)):
			current_cumulative_probability = self.cumulative_function[i]

			while cumulative_probability_counter < current_cumulative_probability:
				self.inverse_cumulative_function.append(self.get_x_value_from_index(i))

				cumulative_probability_counter += (1.0/self.tick_count)

	def get_index_from_cumulative_probability(self, cumulative_probability):
		return int(cumulative_probability*self.tick_count)



	def get_random_value(self):
		"""
		Returns a randomly generated real number that follows the distribution
		"""

		if not self.inverse_cumulative_function:
			raise Exception("The inverse cumulative distribution function has not yet been initialized. Cannot generate a random value.")

		cumulative_probability = np.random.random() #y value of cumulative distribution


		#convert cumulative_probability to be one of ticks
		inverse_cumulative_index = self.get_index_from_cumulative_probability(cumulative_probability)

		x_value = self.inverse_cumulative_function[inverse_cumulative_index] #get corresponding x value

		basic_validators.validate_real_number_is_in_range(x_value, self.min_x, self.max_x)

		return x_value
