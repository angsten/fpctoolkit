

from fpctoolkit.util.path import Path
from fpctoolkit.io.file import File

class Individual(object):
	"""
	Individual for Genetic Algorithm structure searches.
	Just a calculation_set class wrapper with some added functionalities.
	"""

	def __init__(self, calculation_set, structure_creation_id_string=None, parent_structures_list=None, parent_paths_list=None):
		self.calculation_set = calculation_set
		self.structure_creation_id_string = structure_creation_id_string if structure_creation_id_string else self.get_structure_creation_id_string()

		self.parent_structures_list = parent_structures_list if parent_structures_list else self.get_parent_structures_list()
		self.parent_paths_list = parent_paths_list if parent_paths_list else self.get_parent_paths_list()

		self.write_structure_creation_id_string_to_file() #store how this individual was made
		self.write_parent_structures_to_poscar_files()
		self.write_parent_paths_to_file()


	@property
	def energy(self):
		return self.calculation_set.get_final_energy(per_atom=True) 

	@property
	def initial_structure(self):
		return self.calculation_set.initial_structure

	@property
	def complete(self):
		return self.calculation_set.complete

	@property
	def final_structure(self):
		return self.calculation_set.final_structure

	@property
	def how_structure_was_made(self):
		file = File(self.get_structure_creation_id_file_path())
		return file[0]

	def update(self):
		self.calculation_set.update()

	def get_extended_path(self, relative_path):
		return Path.join(self.calculation_set.path, relative_path)

	def get_structure_creation_id_file_path(self):
		return self.get_extended_path('.creation_id')

	def get_structure_creation_id_string(self):
		return File(self.get_structure_creation_id_file_path())[0]

	def get_parent_structures_list(self):
		structure_list = []

		#######implement##################################################
		
		return structure_list

	def get_parent_paths_list(self):
		file = File(".parent_paths")
		paths_list = [line for line in file]
		
		return paths_list

	def write_structure_creation_id_string_to_file(self):
		if self.structure_creation_id_string:
			file = File()
			file += self.structure_creation_id_string
			file.write_to_path(self.get_structure_creation_id_file_path())

	def write_parent_structures_to_poscar_files(self):
		if self.parent_structures_list:
			for i, parent_structure in enumerate(self.parent_structures_list):
				parent_structure.to_poscar_file_path(self.get_extended_path('.parent_poscar_' + str(i) + '.vasp'))

	def write_parent_paths_to_file(self):
		if self.parent_paths_list:
			file = File()

			for path in self.parent_paths_list:
				file += path

			file.write_to_path(self.get_extended_path(".parent_paths"))