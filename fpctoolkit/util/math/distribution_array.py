#from fpctoolkit.util.math.distribution_array import DistributionArray

import numpy as np

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.util.math.distribution import Distribution



class DistributionArray(object):
	"""
	A container holding multiple distribution functions. You can think of a DistributionArray instance as an mxn array of
	random variables, each with potentially distinct distributions.
	"""

	def __init__(self, shape=None):
		"""
		Shape controls the dimensions of the distribution array (rows, cols). One can have arbitrary numbers of dimensions (1, 4, 3, ...).
		To make a 3D vector, shape should be (3). For a 3x3 tensor, set shape to (3, 3).
		"""

		self.shape = shape
		self._distribution_array = np.empty(shape, dtype=object)


	def __len__(self):
		return len(self._distribution_array)

	def set(self, index_tuple, distribution):
		basic_validators.validate_index_tuple(index_tuple, self.shape)

		Distribution.validate_distribution(distribution)

		self._distribution_array.itemset(index_tuple, distribution)

	def get(self, index_tuple):
		basic_validators.validate_index_tuple(index_tuple)

		distribution = self._distribution_array.item(index_tuple)

		Distribution.validate_distribution(distribution)

		return distribution

	def get_flattened_distribution_array(self):
		return np.ndarray.flatten(self._distribution_array)

	def get_random_array(self):
		"""
		For each distribution element of the array, this method calls get_random_value(). These are packed into an array of the same
		shape as this distribution array and returns as a numpy array.
		"""

		self.validate_distribution_array()

		random_values = [distribution.get_random_value() for distribution in self.get_flattened_distribution_array()]

		random_value_array = np.reshape(random_values, self.shape)

		return random_value_array.tolist()


	def validate_distribution_array(self):
		"""
		Ensures that all elements of self._distribution_array are valid distributions.
		"""

		for should_be_a_distribution in self.get_flattened_distribution_array():
			Distribution.validate_distribution(should_be_a_distribution)
