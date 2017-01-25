

from fpctoolkit.io.file import File
from fpctoolkit.io.vasp.outcar import Outcar
from fpctoolkit.io.vasp.potcar import Potcar
from fpctoolkit.util.path import Path
from fpctoolkit.util.queue_adapter import QueueAdapter

class VaspRun(object):
	"""
	Class wrapper for vasp calculations

	"""

	def __init__(self, path, structure=None, incar=None, kpoints=None, potcar=None, submission_script_file=None):
		"""
		If path exists, load files in path, else, files must exist as arguments

		"""
		self.path = Path.clean(path)
		self.structure = structure
		self.incar = incar
		self.kpoints = kpoints
		self.potcar = potcar
		self.submission_script_file = submission_script_file

		if Path.exists(self.path):
			pass
			#see if input files exist - if so, load in?
		else:
			Path.make(self.path)
			self.setup() #writes input files into self.path

	def setup(self):
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

		if not self.submission_script_file:
			self.submission_script_file = QueueAdapter.get_submission_file()
		self.submission_script_file.write_to_path(Path.clean(self.path, 'submit.sh'))

		#put in consistency checks here (modify submit script, lreal, potcar and poscar consistent, ...)

	def start(self):
		QueueAdapter.submit(self.path)

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

