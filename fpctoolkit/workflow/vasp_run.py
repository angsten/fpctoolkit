

from fpctoolkit.io.file import File
from fpctoolkit.io.vasp.outcar import Outcar
from fpctoolkit.io.vasp.potcar import Potcar
from fpctoolkit.util.path import Path
from fpctoolkit.util.queue_adapter import QueueAdapter

class VaspRun(object):
	"""
	Class wrapper for vasp calculations. This class is meant to
	be as general as possible - it simply takes in a set of inputs,
	writes them out, and runs the calculation. There are no
	internal consistency checks done on the inputs. There is,
	however, an error handler that gives updates based on
	the outcar errors present.

	"""

	def __init__(self, path, structure=None, incar=None, kpoints=None, potcar=None, submission_script_file=None, input_set=None):
		"""
		If path directory already exists, load files in path, otherwise, files must exist as arguments

		"""
		self.path = Path.clean(path)

		if input_set:
			structure = input_set.structure
			incar = input_set.incar
			kpoints = input_set.kpoints
			potcar = input_set.potcar
			submission_script_file = input_set.submission_script_file

		self.structure = structure
		self.incar = incar
		self.kpoints = kpoints
		self.potcar = potcar
		self.submission_script_file = submission_script_file

		self.job_id = None #Tracks job id associated with run on queue

		if Path.exists(self.path):
			pass
			#see if input files exist - if so, load in?
			#maybe have an override option
			#if no override, search for saved run and load that class?
		else:
			Path.make(self.path)
			self.setup() #writes input files into self.path

	def setup(self):
		"""
		Simply write files to path
		"""

		self.structure.to_poscar_file_path(Path.clean(self.path, 'POSCAR'))
		self.incar.write_to_path(Path.clean(self.path, 'INCAR'))
		self.kpoints.write_to_path(Path.clean(self.path, 'KPOINTS'))
		self.potcar.write_to_path(Path.clean(self.path, 'POTCAR'))
		self.submission_script_file.write_to_path(Path.clean(self.path, 'submit.sh'))

		#don't...put in consistency checks here (modify submit script, lreal, potcar and poscar consistent, ...)

	def start(self):
		self.job_id = QueueAdapter.submit(self.path)

		#Remove all output files here!!! Maybe store in .folder?

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
		return self.outcar.complete #not necessarily sufficient! what if outcar is old! (remove output files at start)

