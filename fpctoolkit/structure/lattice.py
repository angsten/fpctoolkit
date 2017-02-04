import copy

import numpy as np

class Lattice(object):
	"""Abstract lattice class (2D array)

	a, b, c attributes are access the three lattice vectors
	"""

	def __init__(self, lattice=None, a=None, b=None, c=None):
		"""Lattice can be a Lattice instance or a 2D array"""

		if lattice:
			self.from_2D_array(lattice)
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

	def from_2D_array(self, array):
		self.a = array[0]
		self.b = array[1]
		self.c = array[2]

	def to_array(self):
		return [self.a, self.b, self.c]

	@property
	def np_array(self):
		return np.array(self.to_array())

	def randomly_strain(self, stdev, mask_array=[[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]):
		"""
		Randomly strains using normal distributions for strains

		mask_array is a 2D array that gets multiplied by strain component by component (use 0 or 1 to mask)
		"""

		strain_tensor = []
		strain_tensor.append([np.random.normal(0.0, stdev),     np.random.normal(0.0, stdev)/2.0, np.random.normal(0.0, stdev)/2.0])
		strain_tensor.append([np.random.normal(0.0, stdev)/2.0, np.random.normal(0.0, stdev),     np.random.normal(0.0, stdev)/2.0])
		strain_tensor.append([np.random.normal(0.0, stdev)/2.0, np.random.normal(0.0, stdev)/2.0, np.random.normal(0.0, stdev)])

		for i in range(3):
			for j in range(3):
				strain_tensor[i][j] = strain_tensor[i][j]*mask_array[i][j]

		for i in range(3):
			strain_tensor[i][i] += 1.0

		self.strain(strain_tensor)

	def strain(self, strain_tensor, upper_triangle_only=False):
		"""
		Argument strain_tensor can be a 6x6 full tensor or a 6x1 Voigt-notated tensor

		Note: 1 is not automatically added to the diagonal components of the strain tensor.

								| e11 e12 e13 |
		full tensor looks like:	| e21 e22 e23 |
								| e31 e32 e33 |

		voigt equivalent is: (e11, e22, e33, 2*e23, 2*e13, 2*e12)

		##not supported yet: If upper_triangle_only is True, e21, e31, and e32!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		"""

		strain_tensor = np.array(strain_tensor)
		lattice_matrix = self.np_array

		if strain_tensor.ndim == 1: #voigt notation [e1, e2, e3, e4, e5, e6]
			strain_tensor = Lattice.convert_voigt_strain_to_6x6_tensor(strain_tensor)


		strained_lattice = np.dot(lattice_matrix.T, strain_tensor).T

		self.from_2D_array(strained_lattice)

	def get_super_lattice(self, supercell_dimensions_list):
		"""Returns new lattice that is a super lattice by dimensions supercell_dimensions_list"""

		if not len(supercell_dimensions_list) == 3:
			raise Exception("supercell_dimensions_list must be of length 3")

		new_lattice = copy.deepcopy(self.to_array())

		for i in range(3):
			for j in range(3):
				new_lattice[i][j] *= supercell_dimensions_list[i]

		return Lattice(new_lattice)

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