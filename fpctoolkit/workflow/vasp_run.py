

from fpctoolkit.io.file import File
from fpctoolkit.io.outcar import Outcar
from fpctoolkit.io.potcar import Potcar
from fpctoolkit.util.path import Path

class VaspRun(object):
	"""
	Class wrapper for vasp calculations

	"""

	def __init__(self, path, structure=None, incar=None, kpoints=None, potcar=None, submission_script_file=None):
		"""
		If path exists, load files in path, else, files must exist as arguments

		"""
		self.structure = structure
		self.incar = incar
		self.kpoints = kpoints
		self.potcar = potcar

	def start(self):
		"""
		Verify input files are consistent with each other, write files to path and submit run to queue
		If no potcar, auto generate
		"""
		self.structure.to_poscar_file_path(Path.clean(self.path, 'POSCAR'))
		self.incar.write_to_path(Path.clean(self.path, 'INCAR'))
		self.kpoints.write_to_path(Path.clean(self.path, 'KPOINTS'))

		if not self.potcar:
			self.potcar = Potcar(elements_list=self.structure.get_species_list())

		self.potcar.write_to_path(Path.clean(self.path, 'POTCAR'))


		#put in consistency checks here (potcar and poscar consistent, ...)

		#submit job here

	def update(self):
		"""Check job status on queue. Check for errors"""
		pass

	def stop(self):
		"""If run has associated job on queue, delete this job"""
		pass

	@property
	def outcar(self):
		return Outcar(Path.clean(self.path, 'OUTCAR'))

	@property
	def complete(self):
		return self.outcar.complete #not necessarily sufficient! what if outcar is old!

