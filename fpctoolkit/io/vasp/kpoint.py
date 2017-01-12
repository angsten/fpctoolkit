

from fpctoolkit.io.file import File

class Kpoint(File):
	
	@property
	def scheme(self):
		scheme_line = self[2]
		if scheme_line[0] == 'G':
			return 'Gamma'
		elif scheme_line[0] == 'M':
			return 'Monkhorst'

	@scheme.setter
	def scheme(self, value):
		self[2] = value.rstrip() + "\n"

	@property
	def subdivisions_list(self):
		subdivision_list_line = self[3].rstrip()
		return [int(x) for x in subdivision_list_line.split(' ')]

	@subdivisions_list.setter
	def subdivisions_list(self, value):
		self[3] = " ".join(str(x) for x in value) + "\n"
