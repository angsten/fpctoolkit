#from fpctoolkit.structure_prediction.individual import Individual

from fpctoolkit.util.path import Path
from fpctoolkit.io.file import File
from fpctoolkit.structure.structure import Structure

class Individual(object):
	"""
	Individual for Genetic Algorithm structure searches.
	Just a calculation_set class wrapper with some added functionalities.
	"""

	def __init__(self, path=None, calculation_set=None, structure_creation_id_string=None, parent_structures_list=None, parent_paths_list=None):


		if not calculation_set:
			if not path:
				raise Exception("Path must be given if no calculation set is provided.")

			self.path = path
			self.load()
		else:
			self.path = calculation_set.path
			self.calculation_set = calculation_set

			self.structure_creation_id_string = structure_creation_id_string if structure_creation_id_string else self.get_structure_creation_id_string()
			self.parent_structures_list = parent_structures_list if parent_structures_list else self.get_parent_structures_list()
			self.parent_paths_list = parent_paths_list if parent_paths_list else self.get_parent_paths_list()

			self.write_structure_creation_id_string_to_file() #store how this individual was made
			self.write_parent_structures_to_poscar_files()
			self.write_parent_paths_to_file()

			self.save()

	@property
	def complete(self):
		return self.calculation_set.complete

	@property
	def energy(self):
		return self.calculation_set.get_final_energy(per_atom=True) 

	@property
	def initial_structure(self):
		return self.calculation_set.initial_structure

	@property
	def final_structure(self):
		return self.calculation_set.final_structure

	def update(self):
		self.calculation_set.update()

	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)

	def get_structure_creation_id_file_path(self):
		return self.get_extended_path('.creation_id')

	def get_structure_creation_id_string(self):
		if not Path.exists(self.get_structure_creation_id_file_path()):
			return None
		else:
			file = File(self.get_structure_creation_id_file_path())

		if len(file) < 1:
			return None
		else:
			return file[0]

	def get_parent_structures_list(self):
		structure_list = []

		i = 0
		while True:
			parent_path = self.get_extended_path('.parent_poscar_' + str(i) + '.vasp')

			if Path.exists(parent_path):
				structure_list.append(Structure(parent_path))
				i += 1
			else:
				break
		
		return structure_list

	def get_parent_paths_list(self):
		if Path.exists(self.get_extended_path(".parent_paths")):
			file = File(self.get_extended_path(".parent_paths"))
			paths_list = [line for line in file]

			return paths_list
		else:
			return None

	def write_structure_creation_id_string_to_file(self):
		if self.structure_creation_id_string:
			file = File()
			file += self.structure_creation_id_string
			file.write_to_path(self.get_structure_creation_id_file_path())

	def write_parent_structures_to_poscar_files(self):
		if self.parent_structures_list and (not Path.exists(self.get_extended_path(".parent_paths"))):
			for i, parent_structure in enumerate(self.parent_structures_list):
				parent_structure.to_poscar_file_path(self.get_extended_path('.parent_poscar_' + str(i) + '.vasp'))

	def write_parent_paths_to_file(self):
		if self.parent_paths_list:
			file = File()

			for path in self.parent_paths_list:
				file += path

			file.write_to_path(self.get_extended_path(".parent_paths"))


	def save(self):
		"""Saves self to a pickled file"""

		file = open(self.get_save_path(), 'w')
		file.write(cPickle.dumps(self.__dict__))
		file.close()

	def load(self):
		"""
		Loads the previously saved pickled instance of self at self.path.
		"""

		if not Path.exists(self.get_save_path()):
			raise Exception("Cannot load individual: no instance saved to file.")

		file = open(self.get_save_path(), 'r')
		data_pickle = file.read()
		file.close()

		self.__dict__ = cPickle.loads(data_pickle)

	def get_save_path(self):
		return self.get_extended_path(".individual_pickle")