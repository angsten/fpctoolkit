



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