#from fpctoolkit.phonon.normal_coordinate import NormalCoordinate

import numpy as np
from collections import OrderedDict
import copy

import fpctoolkit.util.basic_validators as basic_validators


class NormalCoordinate(object):
	"""
	Represents one of the two parts of the 'complex normal coordinate', Q_q,j (see around page 298 of Born and Huang and pages preceding). 
	These coordinates effectively the amplitude of a normal mode eigenvector distortion.

	Here, we represent the complex normal coordinate Q_q,j as a real and imaginary part, qsup(y, j)sub(lambda=1)+i*qsup(y,j)sub(lambda=2)

	This class stores a pointer to the relevant normal mode to which this coordinate applies as well as the super displacement vector.
	"""

	def __init__(self, normal_mode_instance, lambda_index, coefficient, phonon_super_displacement_vector_instance):
		"""
		"""

		basic_validators.validate_real_number(coefficient)

		if lambda_index not in [1, 2]:
			raise Exception("Lambda index must either be one (for real complex normal coordinate component) or two (for imaginary):", lambda_index)


		self.coefficient = coefficient
		self.lambda_index = lambda_index
		self.normal_mode = normal_mode_instance
		self.normal_mode_displacement_vector = phonon_super_displacement_vector_instance


	def __str__(self):
		return str(self.coefficient) + " q=" + str(self.q_vector) + ", band=" + str(self.band_index+1) + ", lambda=" + str(self.lambda_index) + ", eigenvalue=" + str(round(self.normal_mode.eigenvalue, 3))

	@property
	def q_vector(self):
		"""
		Returns fractional coordinate q vector tuple like (0.0, 0.5, 0.25).
		"""

		return self.normal_mode.q_point_fractional_coordinates

	@property
	def band_index(self):
		"""
		Returns a band index between 0 and Nat-1.
		"""

		return self.normal_mode.band_index

	@property
	def frequency(self):

		return self.normal_mode.frequency


	def get_displacement_vector(self):
		"""
		Returns a DisplacementVector instance which is obtained by multiplying the normal mode displacement pattern in 
		self.normal_mode_displacement_vector by this instances self.coefficient value.
		"""

		phonon_displacement_vector_instance = copy.deepcopy(self.normal_mode_displacement_vector)

		phonon_displacement_vector_instance *= self.coefficient

		return phonon_displacement_vector_instance

