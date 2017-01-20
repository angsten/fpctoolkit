

from fpctoolkit.io.file import File
import fpctoolkit.util.string_util as su

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
		species_line = su.remove_extra_spaces(self[5])
		return species_line.split(' ')

	@species_list.setter
	def species_list(self):
		pass

	@property
	def species_count_list(self):
		species_count_line = su.remove_extra_spaces(self[6])
		return [int(species_count) for species_count in species_count_line.split(' ')]

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

	@property
	def coordinates(self):
		coordinates = []
		index = 8

		for line in self[8:]:
			coordinate = Poscar.get_coordinate_from_line(line)

			if not coordinate:
				break
			else:
				coordinates.append(coordinate)

		return coordinates

	def validate_lines(self):
		if float(self[1].strip()) != 1.0:
			raise Exception("Scaling factor in poscar not supported.")

		if (self[7].upper()).find('SELECTIVE') != -1:
			raise Exception("Selective dynamics not yet supported")

	@staticmethod
	def get_coordinate_from_line(line_string):
		line_string = su.remove_extra_spaces(line_string).strip()
		component_strings = line_string.split(' ')
		if len(component_strings) != 3:
			return False

		try:
			coordinate = [float(component) for component in component_strings]
		except ValueError:
			return False

		return coordinate