

import numpy as np

class Lattice(object):
	"""Abstract lattice class (2D array)

	a, b, c attributes are access the three lattice vectors
	"""

	def __init__(self, lattice=None, a=None, b=None, c=None):
		"""Lattice can be a Lattice instance or a 2D array"""

		if lattice:
			self.a = lattice[0]
			self.b = lattice[1]
			self.c = lattice[2]
		else:
			self.a = a
			self.b = b
			self.c = c

	def __str__(self):
		return " ".join(str(x) for x in self.a) + '\n' + " ".join(str(x) for x in self.b) + '\n' + " ".join(str(x) for x in self.c) + '\n'


	def __getitem__(self, key):
		if isinstance(key, int) and key >= 0 and key <= 2:
			if key == 0:
				return self.a
			elif key == 1:
				return self.b
			elif key == 2:
				return self.c
		else:
			raise KeyError

	def to_array(self):
		return [self.a, self.b, self.c]

	@property
	def np_array(self):
		return np.array(self.to_array())

	def randomly_strain(self, stdev):
		"""Randomly strains using normal distributions for strains of e1, e2, e3, e4, e5, and e6"""

		pass

	def strain(self, strain_tensor):
		"""
		Argument strain_tensor can be a 6x6 full tensor or a 6x1 Voigt-notated tensor

		Note: 1 is not automatically added to the diagonal components of the strain tensor.
		"""

		strain_tensor = np.array(strain_tensor)
		lattice_matrix = self.np_array

		if strain_tensor.ndim == 1: #voigt notation [e1, e2, e3, e4, e5, e6]
			strain_tensor = Lattice.convert_voigt_strain_to_6x6_tensor(strain_tensor)

		strained_lattice = np.dot(lattice_matrix.T, strain_tensor).T



		return strained_lattice

	@staticmethod
	def convert_voigt_strain_to_6x6_tensor(voigt_tensor):
		"""Converts [e1, e2, e3, e4, e5, e6] to [[e1, e6/2, e5/2], [e6/2, e2, e4/2], [e5/2, e4/2, e3]]"""
		if not len(voigt_tensor) == 6:
			raise Exception("Voigt tensor must have six components")

		voigt_tensor = np.array(voigt_tensor)
		if not voigt_tensor.ndim == 1:
			raise Exception("Number of array dimensions of voigt tensor must be 1")

		full_tensor = []

		full_tensor.append([voigt_tensor[0], voigt_tensor[5]/2.0, voigt_tensor[4]/2.0])
		full_tensor.append([voigt_tensor[5]/2.0, voigt_tensor[1], voigt_tensor[3]/2.0])
		full_tensor.append([voigt_tensor[4]/2.0, voigt_tensor[3]/2.0, voigt_tensor[2]])

		return np.array(full_tensor)