

from fpctoolkit.io.vasp.potcar import Potcar
from fpctoolkit.util.queue_adapter import QueueAdapter

class VaspInputSet(object):
	"""Holds the set of four basic vasp input files + submit script in a list

	Note, the poscar is not considered a basic input file - structure class is.
	This is okay because there is always a clear one to one mapping.

	Contains many helper functions to auto-create these inputs and ensure consistency
	between them

	"""

	def __init__(self, structure=None, kpoints=None, incar=None, potcar=None, submission_script_file=None):
		self.structure = structure
		self.incar = incar
		self.kpoints = kpoints
		self.potcar = potcar
		self.submission_script_file = submission_script_file

		if (not self.potcar) and self.structure:
			self.auto_generate_potcar()

		if not self.submission_script_file:
			self.submission_script_file = QueueAdapter.get_submission_file()

		if self.structure:
			self.check_potcar_structure_consistency()
			self.set_number_of_cores_from_structure()

	def auto_generate_potcar(self):
		if not self.structure:
			raise Exception("Structure must be defined in order to make potcar")
		else:
			self.potcar = Potcar(elements_list=self.structure.get_species_list())

	def check_potcar_structure_consistency(self):
		if not self.potcar.get_elements_list() == self.structure.get_species_list():
			raise Exception("Potcar elements list is not compatible with structure")

	def set_number_of_cores_from_structure(self):
		"""Looks at number of atoms in structure and sets the number of cores in the
		submission script accordingly
		"""

		self.submission_script_file = 
