#from fpctoolkit.structure.lattice import Lattice

import copy
import numpy as np

from fpctoolkit.util.tensor import Tensor

class Lattice(object):
	"""
	Class for representing a lattice (effectively just a 3x3 2D array of floating point numbers). This class can be modified or acessed in the
	same way as a 2D array (lattice[i][j] = ..., b_x = lattice[1][0]).

	The a, b, and c attributes hold the three lattice vectors.

	To get the b lattice vector of instance lattice, one can use lattice.b or lattice[1]

	To get a 2D array representation, one can use lattice.to_array() or lattice.to_np_array()

	To modify, for example, a_y, one can use lattice[0][1] = 0.2.
	"""

	def __init__(self, lattice=None):
		"""
		lattice can be a Lattice instance, a 3x3 2D array of floats, or left as None. Deep copies are made in the first two cases.

		If lattice is None, then a lattice with all zeros is created.
		"""
		print "in lattice init. input lattice looks like: ", lattice

		if not lattice:
			lattice = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]

		if not Lattice.lattice_representation_is_compatible(lattice):
			raise Exception("The provided lattice argument is not in a form compatible with a lattice. Input lattice looks like: " + str(array))

		self.from_2D_array(lattice)

		print "testing attribute a", self.a


	def from_2D_array(self, array):
		"""
		Load a 2D list (array) into self.a, b, and c. First, it is ensured that array is compatible with a lattice.
		"""

		self.a = copy.deepcopy(array[0])
		self.b = copy.deepcopy(array[1])
		self.c = copy.deepcopy(array[2])


	def __str__(self):
		return " ".join(str(x) for x in self.a) + '\n' + " ".join(str(x) for x in self.b) + '\n' + " ".join(str(x) for x in self.c) + '\n'


	def __getitem__(self, key):
		"""
		For an instance lattice, one can write lattice[0] to get the a lattice vector, lattice[1] for b, ...
		"""

		if isinstance(key, int) and (key >= 0 and key <= 2):
			if key == 0:
				return self.a
			elif key == 1:
				return self.b
			elif key == 2:
				return self.c
		else:
			raise KeyError

	def to_array(self):
		"""
		Returns lattice as a 3x3 list of lists that looks like:

		[[a1, a2, a3], 
		 [b1, b2, b3], 
		 [c1, c2, c3]]
		"""

		return [self.a, self.b, self.c]

	def to_np_array(self):
		"""
		Returns lattice as a 3x3 numpy array
		"""

		return np.array(self.to_array())


	def get_super_lattice(self, supercell_dimensions_list):
		"""
		Returns new Lattice instance that is a super lattice by dimensions supercell_dimensions_list. 

		With supercell_dimensions_list = [2, 1, 1], all components of the a lattice vector will be doubled. 

		Does not modify self.
		"""

		if (not isinstance(supercell_dimensions_list, list)) or (len(supercell_dimensions_list) != 3):
			raise Exception("supercell_dimensions_list must be of length 3")


		new_lattice = Lattice(self) #makes a deep copy

		for i in range(3):
			for j in range(3):
				new_lattice[i][j] *= supercell_dimensions_list[i]

		return new_lattice




	def strain(self, strain_tensor):
		"""
		Strains self (in place) by the tensor strain_tensor. The strain tensor should take the form of a deformation gradiation tensor F (doesn't have to be symmetric). See examples below.

		Argument strain_tensor can be a 3x3 tensor or a 1x6 Voigt-notated tensor

		Note: 1.0 is not automatically added to the diagonal components of the strain tensor.

								| e11 e12 e13 |
		full tensor looks like:	| e21 e22 e23 |      where e12 = (dx_1/dX_2), the constant factor by which the x component of a vector (in new coordinates) is displaced per y component in original coordinates.
								| e31 e32 e33 |      e12 would then correspond to a shear strain applied on the y-plane in the x direction.

		voigt equivalent is: (e11, e22, e33, 2*e23, 2*e13, 2*e12)

		For an original vecotr a, the strain tensor will take it to a new vector a' given by:

		a'_x = a_x*e11 + a_y*e12 + a_z*e13
		a'_y = a_x*e21 + a_y*e22 + a_z*e23
		a'_z = a_x*e31 + a_y*e32 + a_z*e33

		Another example: if e12 (a shear applied to the y-plane in the x direction) is 0.1, and if b was originally [0.0, 10.0, 0.0], the new b vector after shearing will be [1.0, 10.0, 0.0]

		If the strain tensor is the identity matrix, the lattice will not change.
		"""

		original_lattice_matrix = self.to_np_array()
		strain_tensor = np.array(strain_tensor)
		
		if strain_tensor.ndim == 1:
			strain_tensor = Tensor.convert_voigt_strain_to_3x3_tensor(strain_tensor)


		strained_lattice = np.dot(original_lattice_matrix, strain_tensor.T)

		self.from_2D_array(strained_lattice)


	def randomly_strain(self, distribution_function_array):
		"""
		Randomly strains self (in place) using the given distribution_function_array.

		distribution_function_array should be a 3x3 array of functions that, when called, supply the corresponding randomly produced strain components.
		"""

		strain_tensor = []
		strain_tensor.append([distribution_function_array[0][0](), distribution_function_array[0][1](), distribution_function_array[0][2]()])
		strain_tensor.append([distribution_function_array[1][0](), distribution_function_array[1][1](), distribution_function_array[1][2]()])
		strain_tensor.append([distribution_function_array[2][0](), distribution_function_array[2][1](), distribution_function_array[2][2]()])

		self.strain(strain_tensor)



	@staticmethod
	def average(lattice_1, lattice_2, weight=0.5):
		"""
		Returns a lattice which is the weighted arithmetic average of lattice_1 and lattice_2.

		lattice_1 and lattice_2 can be Lattice instances or compatible 2D lists.

		weight must be in range [0.0, 1.0] and larger weight means more lattice_1 representation in average.
		"""

		if (weight < 0.0) or (weight > 1.0):
			raise Exception("Weighting factor must be between zero and one inclusive.")

		if not (Lattice.lattice_representation_is_compatible(lattice_1) and Lattice.lattice_representation_is_compatible(lattice_2)):
			raise Exception("Input lattices are not both compatible representations. lattice_1: " + str(lattice_1) + "   lattice_2: " + str(lattice_2))


		new_lattice = Lattice()

		for i in range(3):
			for j in range(3):
				new_lattice[i][j] = weight*lattice_1[i][j] + (1.0-weight)*lattice_2[i][j]

		return new_lattice


	@staticmethod
	def lattice_representation_is_compatible(lattice_representation):
		"""
		Returns True if lattice_representation can represent a lattice (i.e. contains floats, is of dimension two and length 3 for both lists) or is a Lattice class instance, else False.
		"""

		if isinstance(lattice_representation, Lattice):
			return True

		if not isinstance(lattice_representation, (np.ndarray, list)):
			return False

		if len(lattice_representation) != 3:
			return False

		for i in range(3):
			if not isinstance(lattice_representation[i], (np.ndarray, list)):
				return False

			if len(lattice_representation[i]) != 3:
				return False

			for j in range(3):
				if (not isinstance(lattice_representation[i][j], float)) and (not isinstance(lattice_representation[i][j], int)):
					return False

		return True