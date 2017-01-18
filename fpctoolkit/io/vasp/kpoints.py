import string

from fpctoolkit.io.file import File

class Kpoints(File):
	"""
	properties:
		scheme ('Monkhorst' or 'Gamma')
		subdivisions_list ([1,2,5] or [4,4,6])
	"""

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

		return [int(x) for x in subdivision_list_line.split(' ')]

	@subdivisions_list.setter
	def subdivisions_list(self, value):
		self[3] = " ".join(str(x) for x in value)


	@staticmethod
	def parse_scheme(scheme_str):
		if string.upper(scheme_str[0]) == 'G':
			return 'Gamma'
		elif string.upper(scheme_str[0]) == 'M':
			return 'Monkhorst'
		else:
			raise Exception("Kpoints scheme not set properly. Must start with M or G.")