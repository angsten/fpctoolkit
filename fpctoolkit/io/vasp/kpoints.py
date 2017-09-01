import string

from fpctoolkit.io.file import File

class Kpoints(File):
	"""
	properties:
		scheme ('Monkhorst' or 'Gamma')
		subdivisions_list ([1,2,5] or [4,4,6])
	"""

	def __init__(self, file_path=None, scheme_string=None, subdivisions_list=None, kspacing=None, lattice=None):

		super(Kpoints, self).__init__(file_path)

		if file_path:
			self.scheme #running these lines validates properties
			self.subdivisions_list
		elif not kspacing:
			self[0] = "Kpoints File"
			self[1] = "0"
			self.scheme = scheme_string
			self.subdivisions_list = subdivisions_list
			self += "0 0 0"
		else:
			self.set_subdivisions_from_kspacing(kspacing, lattice)


	@property
	def scheme(self):
		scheme_line = self[2]
		return Kpoints.parse_scheme(scheme_line)


	@scheme.setter
	def scheme(self, value):
		self[2] = Kpoints.parse_scheme(value)

	@property
	def subdivisions_list(self):
		subdivision_list_line = self[3].rstrip()

		subdivisions_list = [int(x) for x in subdivision_list_line.split(' ')]

		if len(subdivisions_list) != 3:
			raise Exception("Error parsing subdivisions list. List is " + str(subdivisions_list))

		return subdivisions_list

	@subdivisions_list.setter
	def subdivisions_list(self, value):
		if len(value) != 3:
			raise Exception("Subdivisions_list length must be 3. Value given is " + str(value))

		self[3] = " ".join(str(x) for x in value)

	def set_subdivisions_list_from_kspacing(kspacing=None, lattice=None):
		"""kspacing is given in inverse angstroms"""
		return None


	@staticmethod
	def parse_scheme(scheme_string):
		if string.upper(scheme_string[0]) == 'G':
			return 'Gamma'
		elif string.upper(scheme_string[0]) == 'M':
			return 'Monkhorst'
		else:
			raise Exception("Kpoints scheme not set properly. Must start with M or G.")