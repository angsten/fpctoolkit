#from fpctoolkit.util.math.tensor import Tensor

import numpy as np



class Tensor(object):
	"""
	Defines convenience static methods relevant to tensors.
	"""

	@staticmethod
	def convert_voigt_strain_to_3x3_tensor(voigt_tensor):
		"""
		Converts 1x6 like [e1, e2, e3, e4, e5, e6] to 3x3 like [[e1, e6/2, e5/2], [e6/2, e2, e4/2], [e5/2, e4/2, e3]] (as a numpy array)
		"""

		voigt_tensor = np.array(voigt_tensor)

		if not voigt_tensor.ndim == 1:
			raise Exception("Number of array dimensions of voigt tensor must be 1. Input tensor: " + str(voigt_tensor))

		if not len(voigt_tensor) == 6:
			raise Exception("Voigt tensor must have six components. Input tensor: " + str(voigt_tensor))

		full_tensor = []

		full_tensor.append([voigt_tensor[0], voigt_tensor[5]/2.0, voigt_tensor[4]/2.0])
		full_tensor.append([voigt_tensor[5]/2.0, voigt_tensor[1], voigt_tensor[3]/2.0])
		full_tensor.append([voigt_tensor[4]/2.0, voigt_tensor[3]/2.0, voigt_tensor[2]])

		return np.array(full_tensor)