#from fpctoolkit.phonon.normal_coordinate import NormalCoordinate

import numpy as np
from collections import OrderedDict

import fpctoolkit.util.basic_validators as basic_validators


class NormalCoordinate(object):
	"""
	Represents a 'complex normal coordinate', Q_q,j (see around page 298 of Born and Huang and pages preceding). This is effectively the
	amplitude of a normal mode eigenvector distortion.

	This class stores a complex coefficient and a pointer to the relevant normal mode to which this coordinate applies.
	"""

	def __init__(self, normal_mode_instance, complex_coefficient=0.0+0.0j):
		"""
		"""

		basic_validators.validate_complex_number(complex_coefficient)


		self.complex_coefficient = complex_coefficient

		self.normal_mode = normal_mode_instance
