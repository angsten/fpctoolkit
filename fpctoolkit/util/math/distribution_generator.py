#from fpctoolkit.util.math.distribution_generator import DistributionGenerator

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.util.math.distribution import Distribution



class DistributionGenerator(object):
	"""
	Defines staticmethods for returning various distributions.
	"""

	@staticmethod
	def get_zero_distribution():
		"""
		Returns a distribution that always returns zero.
		"""

		return Distribution(shape_function=lambda x: 1.0, min_x=0.0, max_x=0.0, tick_count=1)


	@staticmethod
	def get_unity_distribution():
		"""
		Returns a distribution that always returns one.
		"""

		return Distribution(shape_function=lambda x: 1.0, min_x=1.0, max_x=1.0, tick_count=1)


	@staticmethod
	def get_uniform_distribution(min_x, max_x):
		"""
		Returns a uniform distribution that generates values from min_x to max_x evenly.
		"""

		basic_validators.validate_first_real_number_is_strictly_less_than_or_equal_to_second(min_x, max_x)

		return Distribution(shape_function=lambda x: 1.0, min_x=min_x, max_x=max_x)