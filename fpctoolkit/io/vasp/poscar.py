

from fpctoolkit.io.file import File

class Poscar(File):
	"""Just a file container - for more methods see Structure class

		Selective dynamics not yet supported

		lattice (2-4)
		species_list (5)
		species_count_list (6)
		coord_system (7) (could be select dyn)
		coordinates (8+)
	"""

	def __init__(self, file_path=None):

		super(Poscar, self).__init__(file_path)

		if file_path:
			self.validate_lines()
		else:
			self[0] = 'Poscar'
			self[1] = '1.0'


	@property
	def lattice(self):
		lattice_lines_list = self[2:5]
		lattice_lines_list = [' '.join(lattice_line.split()) for lattice_line in lattice_lines_list]
		lattice = [[float(lattice_component) for lattice_component in lattice_line.split(' ')] for lattice_line in lattice_lines_list]

		for lattice_components_list in lattice:
			if len(lattice_components_list) != 3:
				raise Exception('Too many components in poscar lattice.')

		return lattice

	@lattice.setter
	def lattice(self):
		pass

	@property
	def species_list(self):
		species_line_no_whitespace = ' '.join(self[5].split())
		return species_line_no_whitespace.split(' ')

	@species_list.setter
	def species_list(self):
		pass

	@property
	def species_count_list(self):
		species_count_line_no_whitespace = ' '.join(self[6].split())
		return [int(species_count) for species_count in species_count_line_no_whitespace.split(' ')]

	@species_count_list.setter
	def species_count_list(self):
		pass

	@property
	def coordinate_system(self):
		coord_sys_line = self[7]
		if 'D' in coord_sys_line.upper():
			return 'Direct'
		elif 'C' in coord_sys_line.upper():
			return 'Cartesian'
		else:
			raise Exception("Coordinate system not valid in poscar line 7: " + coord_sys_line)

	@coordinate_system.setter
	def coordinate_system(self):
		pass


	def validate_lines(self):
		if float(self[1].strip()) != 1.0:
			raise Exception("Scaling factor in poscar not supported.")

		if (self[7].upper()).find('SELECTIVE') != -1:
			raise Exception("Selective dynamics not yet supported")