#from fpctoolkit.phonon.eigen_structure import EigenStructure

import numpy as np
import copy

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.phonon.hessian import Hessian


class EigenStructure(object):
	"""
	Represents a structure whose displacements are relative to a reference structure in terms of six strains (Voigt) and N displacement modes, where N is the number
	of atoms in the reference structure. The displacement modes are the eigen vectors of the hessian matrix for the reference structure.
	"""

	def __init__(self, reference_structure, Hessian):
		"""
		"""

		