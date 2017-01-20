

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
		lattice_component_strings_list = [' '.join(lattice_line.split()) for lattice_line in lattice_lines_list]
		lattice = [[float(lattice_component) for lattice_component in lattice_line.split(' ')] for lattice_line in lattice_component_strings_list]

		Poscar.validate_lattice(lattice)

		return lattice

	@lattice.setter
	def lattice(self, lattice):
		Poscar.validate_lattice(lattice)
		lattice_component_strings_list = [[str(component) for component in components] for components in lattice]
		lattice_lines_list = [' '.join(lattice_component_string) for lattice_component_string in lattice_component_strings_list]

		self.lines[2:5] = lattice_lines_list

	@property
	def species_list(self):
		species_line = su.remove_extra_spaces(self[5])
		return species_line.split(' ')

	@species_list.setter
	def species_list(self, species_list):
		species_list = [species[0].upper()+species[1:].lower() for species in species_list] #'bA' => 'Ba'
		self[5] = ' '.join(species_list)

	@property
	def species_count_list(self):
		species_count_line = su.remove_extra_spaces(self[6])
		return [int(species_count) for species_count in species_count_line.split(' ')]

	@species_count_list.setter
	def species_count_list(self, species_count_list):
		self[6] = ' '.join([str(species_count) for species_count in species_count_list])

	@property
	def coordinate_system(self):
		coord_sys_line = self[7]
		return Poscar.get_coordinate_system_string(coord_sys_line)

	@coordinate_system.setter
	def coordinate_system(self, coordinate_system_string):
		self[7] = Poscar.get_coordinate_system_string(coordinate_system_string)

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

		self._coordinates = coordinates

		return self._coordinates

	@coordinates.setter
	def coordinates(self, coordinates):
		for coordinate in coordinates:
			Poscar.validate_coordinate(coordinate)

		self._coordinates = coordinates

	def validate_lines(self):
		if float(self[1].strip()) != 1.0:
			raise Exception("Scaling factor in poscar not supported.")

		if (self[7].upper()).find('SELECTIVE') != -1:
			raise Exception("Selective dynamics not yet supported")

		self.lattice #these will throw exceptions if not set right in file
		self.coordinates


	@staticmethod
	def validate_lattice(lattice):
		for lattice_components_list in lattice:
			if len(lattice_components_list) != 3:
				raise Exception('Incorrect number of components in poscar lattice.')

	@staticmethod
	def get_coordinate_system_string(coord_sys_line):
		if 'D' in coord_sys_line.upper():
			return 'Direct'
		elif 'C' in coord_sys_line.upper():
			return 'Cartesian'
		else:
			raise Exception("Coordinate system not valid in poscar line 7: " + coord_sys_line)

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

	@staticmethod
	def validate_coordinate(coordinate):
		if len(coordinate) != 3:
			raise Exception("Coordinates must hold three components: " + str(coordinate))

		for component in coordinate:
			if not (isinstance(component, float) or isinstance(component, int)):
				raise Exception("Components of coordinates must be floats or ints")