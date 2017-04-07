#from fpctoolkit.util.math.distribution_array import DistributionArray

import numpy as np
import copy

import fpctoolkit.util.basic_validators as basic_validators
import fpctoolkit.util.basic_checks as basic_checks
from fpctoolkit.util.math.distribution import Distribution
from fpctoolkit.util.math.distribution_generator import DistributionGenerator



class DistributionArray(object):
	"""
	A container holding multiple distribution functions. You can think of a DistributionArray instance as an mxn array of
	random variables, each with potentially distinct distributions.
	"""

	def __init__(self, shape=None, distribution_array=None):
		"""
		shape controls the dimensions of the distribution array (rows, cols). One can have arbitrary numbers of dimensions (1, 4, 3, ...).
		To make a 3D vector, shape should be (3). For a 3x3 tensor, set shape to (3, 3).
		"""

		DistributionArray.validate_constructor_arguments(shape, distribution_array)

		if distribution_array:

			distribution_array = DistributionArray.convert_real_numbers_of_array_to_distributions(distribution_array)

			self.shape = copy.deepcopy(distribution_array.shape)
			self._distribution_array = copy.deepcopy(distribution_array)

		else:
			self.shape = shape
			self._distribution_array = np.full(shape, DistributionGenerator.get_zero_distribution(), dtype=object)




	@staticmethod
	def validate_constructor_arguments(shape, distribution_array):
		"""
		Raises an exception if one of the following is true:
		->both shape and distribution_array are defined 
		->if distribution_array contains anything other than real numbers or distribution instances
		->shape is not a valid tuple of positive non-zero integers
		"""

		if bool(shape == None) == bool(distribution_array == None): #exclusive or - cannot define both arguments but also must have at least one
			raise Exception("One and only one of shape and distribution_array must be defined. Inputted shape is:", shape, "inputted distribution_array is", distribution_array)

		if distribution_array:
			for distribution_or_real_number in np.ndarray.flatten(np.array(distribution_array)):
				DistributionArray.validate_real_number_or_distribution(distribution_or_real_number)
		else:
			basic_validators.validate_tuple_of_positive_nonzero_integers(shape)


	@staticmethod
	def validate_real_number_or_distribution(distribution_or_real_number):
		"""
		Raises an exception if distribution_or_real_number is neither a distribution nor a real number.
		"""

		try:
			basic_validators.validate_real_number(distribution_or_real_number)
		except:
			Distribution.validate_distribution(distribution_or_real_number)

	@staticmethod
	def convert_real_numbers_of_array_to_distributions(array_of_distributions_and_real_numbers):
		"""
		Takes an arbitrary array (can be numpy or python sequence) filled with a mix of distribution instances and real numbers and returns a new numpy array with the real
		numbers converted to distributions that give that number with certainty.
		"""

		numpy_array_of_distributions_and_real_numbers = np.array(array_of_distributions_and_real_numbers)

		flattened_numpy_array_of_distributions_and_real_numbers = np.ndarray.flatten(numpy_array_of_distributions_and_real_numbers)

		for i in range(len(flattened_numpy_array_of_distributions_and_real_numbers)):
			real_number_or_distribution = flattened_numpy_array_of_distributions_and_real_numbers[i]

			if basic_checks.is_a_real_number(real_number_or_distribution):
				real_number = real_number_or_distribution

				flattened_numpy_array_of_distributions_and_real_numbers[i] = DistributionGenerator.get_certainly_one_value_distribution(real_number)

		return np.reshape(flattened_numpy_array_of_distributions_and_real_numbers, numpy_array_of_distributions_and_real_numbers.shape)




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

		random_values_list = [distribution.get_random_value() for distribution in self.get_flattened_distribution_array()]

		random_value_array = np.reshape(random_values_list, self.shape)

		return random_value_array.tolist()


	def validate_distribution_array(self):
		"""
		Ensures that all elements of self._distribution_array are valid distributions.
		"""

		for should_be_a_distribution in self.get_flattened_distribution_array():
			Distribution.validate_distribution(should_be_a_distribution)
