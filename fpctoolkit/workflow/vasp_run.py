import cPickle

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
		If path directory already exists, load run saved in path, otherwise, files must exist as arguments

		"""
		self.path = Path.clean(path)

		if Path.exists(self.get_extended_path("RUN_SUBMISSION_UNTRACKED")):
			raise Exception("Previous run had potentially untracked job - check fail file for id and delete if id exists on queue")

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
			#Don't overwrite - load in the run here if it exists
			if Path.exists(self.get_save_path()):
				self.load()
			else:
				#can't find a run to load - overwrite?
				raise Exception("temporory here - load not supported in this way yet")
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

	def update(self):
		"""Check job status on queue. Check for errors"""
		
		#only if there is not job_id associated with this run should we start a run
		if not self.job_id:
			self.start()

	def start(self):
		"""Submit the calculation at self.path"""

		try:
			#Remove all output files here!!! Maybe store in .folder?
			#also, check that this run doesn't already have a job on queue associated with it!

			self.job_id = QueueAdapter.submit_job(self.path)

			self.save() #want to make sure we save here so tracking of job id isn't lost
		except Exception as exception:
			"""
			Submission of a job to the queue has failed.

			This file creation is a safeguard against vasp runs that submit a job
			to the queue, but fail to save (thus losing the id information)
			This is dangerous - could create a rogue run, so must delete the path
			if this file is found.
			"""
			failed_file = File()
			failed_file += str(self.job_id) #this may be None if assignment above failed
			failed_file.write_to_path(self.get_extended_path("RUN_SUBMISSION_UNTRACKED"))

			raise exception #reraise the original exception so the error can be passed on

	def stop(self):
		"""If run has associated job on queue, delete this job"""
		pass

	@property
	def outcar(self):
		return Outcar(Path.clean(self.path, 'OUTCAR'))

	@property
	def complete(self):
		return self.outcar.complete #not necessarily sufficient! what if outcar is old! (remove output files at start)

	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)

	def get_save_path(self):
		return self.get_extended_path(".run_pickle")


	def save(self):
		"""Saves class to pickled file at {self.path}/.run_pickle
		"""

		#We don't want to waste space with storing full potcars - just store basenames and recreate on loading
		self.potcar_minimal_form = self.potcar.get_minimal_form()
		stored_potcar = self.potcar
		self.potcar = None

		save_path = self.get_save_path()

		file = open(save_path, 'w')
		file.write(cPickle.dumps(self.__dict__))
		file.close()

		self.potcar = stored_potcar

	def load(self,load_path=None):
		if not load_path:
			load_path = self.get_save_path()

		if not Path.exists(load_path):
			raise Exception("Load file path does not exist: " + load_path)

		file = open(load_path, 'r')
		data_pickle = file.read()
		file.close()

		self.__dict__ = cPickle.loads(data_pickle)

		#restore the full potcar from the basenames that were saved
		if self.potcar_minimal_form:
			self.potcar = Potcar(minimal_form=self.potcar_minimal_form)
			del self.potcar_minimal_form




	def __str__(self):
		head_string = "==> "
		file_separator = 30*"-"
		output_string = ""

		output_string += 10*"-" + "VaspRun: Job ID is " + str(self.job_id) + 10*"-" + "\n"
		output_string += head_string + "Path: " + self.path + "\n"
		output_string += head_string + "Potcar: " + " ".join(self.potcar.get_titles()) + "\n"
		output_string += head_string + "Kpoints:\n" + file_separator + "\n" + str(self.kpoints) + file_separator + "\n"
		output_string += head_string + "Incar:\n" + file_separator + "\n" + str(self.incar) + file_separator + "\n"
		output_string += head_string + "Structure:\n" + file_separator + "\n" + str(self.structure) + file_separator + "\n"

		return output_string