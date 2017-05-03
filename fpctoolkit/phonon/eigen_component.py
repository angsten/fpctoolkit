#from fpctoolkit.phonon.eigen_component import EigenComponent

import numpy as np
import copy

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.phonon.hessian import Hessian


class EigenComponent(object):
	"""
	Represents a single distortion mode along an eigenvector with an associated amplitude.
	"""

	def __init__(self, eigen_pair_instance, amplitude=0.0):

		basic_validators.validate_real_number(amplitude)

		self.eigen_pair = eigen_pair_instance

		self.amplitude = amplitude


	def get_displacement_vector(self):
		"""
		Return the amplitude*eigenvector to get the resulting set of atomic displacements.
		"""

		return self.amplitude*self.eigenvector

	def is_translational_mode(self):
		return self.eigen_pair.is_translational_mode()

	@property
	def eigenvector(self):
		return self.eigen_pair.eigenvector

	@property
	def eigenvalue(self):
		return self.eigen_pair.eigenvalue
