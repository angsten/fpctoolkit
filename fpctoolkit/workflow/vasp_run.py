import cPickle

from fpctoolkit.io.file import File
from fpctoolkit.io.vasp.outcar import Outcar
from fpctoolkit.io.vasp.potcar import Potcar
from fpctoolkit.io.vasp.incar import Incar
from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.util.path import Path
from fpctoolkit.util.queue_adapter import QueueAdapter, QueueStatus
import fpctoolkit.util.string_util as su

class VaspRun(object):
	"""
	Class wrapper for vasp calculations. This class is meant to
	be as general as possible - it simply takes in a set of inputs,
	writes them out, and runs the calculation. There are no
	internal consistency checks done on the inputs. There is,
	however, an error handler that gives updates based on
	the outcar errors present.

	Can use special_handler if you want to use a custom error handler class (must be child class of VaspHandler class)
	"""

	log_path = ".log"

	def __init__(self, path, structure=None, incar=None, kpoints=None, potcar=None, submission_script_file=None, input_set=None, special_handler=None, verbose=True):
		"""
		If path directory already exists, load run saved in path, otherwise, files must exist as arguments

		"""
		self.path = Path.clean(path)
		self.verbose = verbose

		if special_handler:
			self.handler = special_handler
		else:
			pass #self.handler = VaspHandler()

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

		self.job_id_string = None #Tracks job id associated with run on queue, looks like '35432'

		if Path.exists(self.path) and not Path.is_empty(self.path):
			#We're in a directory with files in it - see if there's an old run to load
			if Path.exists(self.get_save_path()):
				self.log("Run path exists and a saved run file exists.")
				self.load()
			else:
				#Directory has files in it but no saved VaspRun. This case is not yet supported
				self.log("Files present in run directory but no run to load. Not yet supported.", raise_exception=True)
		else:
			Path.make(self.path)

			self.log("Directory at run path did not exist or was empty. Created directory.")

			self.setup() #writes input files into self.path

	def setup(self):
		"""
		Simply write files to path
		"""

		self.log("Writing input files to path.")

		self.structure.to_poscar_file_path(Path.clean(self.path, 'POSCAR'))
		self.incar.write_to_path(Path.clean(self.path, 'INCAR'))
		self.kpoints.write_to_path(Path.clean(self.path, 'KPOINTS'))
		self.potcar.write_to_path(Path.clean(self.path, 'POTCAR'))
		self.submission_script_file.write_to_path(Path.clean(self.path, 'submit.sh'))

		#don't...put in consistency checks here (modify submit script, lreal, potcar and poscar consistent, ...)

	def update(self):
		"""Returns True if run is completed"""
		
		self.log("Updating run")

		#only if there is not job_id_string associated with this run should we start the run
		if not self.job_id_string:
			self.log("No job id stored in this run.")
			self.start()

			return False

		#check if run is complete
		if self.complete:
			self.log("Run is complete.")
			return True

		#check status on queue:
		#if running, check for runtime errors using handler
		#if queued, return false
		#if not on queue, run failed - check for errors using handler

		queue_properties = self.queue_properties
		if not queue_properties: #couldn't find job on queue
			queue_status = None
		else:
			queue_status = queue_properties['status']

		if queue_status == QueueStatus.queued:
			self.log("Job is on queue waiting.")

		elif queue_status == QueueStatus.running:
			self.log("Job is on queue running. Queue properties: " + str(self.queue_properties))

			#use handler to check for run time errors here
		else:
			self.log("Run is not active on queue ('C', 'E', or absent) but still isn't complete. An error must have occured.")

			#use handler to check for errors here


		return False

	def start(self):
		"""Submit the calculation at self.path"""

		self.log("Submitting a new job to queue.")

		#Remove all output files here!!! Maybe store in hidden archived folder?####################???????????????????????????????????????????????????????????????????????????????????????????
		#also, check that this run doesn't already have a job on queue associated with it!

		self.job_id_string = QueueAdapter.submit_job(self.path)

		if not self.job_id_string:
			self.log("Tried to start vasp run but an active job is already associated with its path.", raise_exception=True)

		self.save() #want to make sure we save here so tracking of job id isn't lost

	def stop(self):
		"""If run has associated job on queue, delete this job"""
		
		QueueAdapter.terminate_job(self.job_id_string)

	@property
	def outcar(self):
		outcar_path = Path.clean(self.path, 'OUTCAR')
		if Path.exists(outcar_path):
			return Outcar(outcar_path)
		else:
			return None

	@property
	def complete(self):
		outcar = self.outcar

		if outcar:
			return outcar.complete #not necessarily sufficient! what if outcar is old! (remove output files at start)
		else:
			return False

	@property
	def queue_properties(self):
		if not self.job_id_string:
			return None
		else:
			return QueueAdapter.get_job_properties_from_id_string(self.job_id_string)

	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)

	def get_save_path(self):
		return self.get_extended_path(".run_pickle")


	def save(self):
		"""Saves class to pickled file at {self.path}/.run_pickle
		"""

		self.log("Saving run")

		#We don't want to waste space with storing full potcars - just store basenames and recreate on loading
		self.potcar_minimal_form = self.potcar.get_minimal_form()
		stored_potcar = self.potcar
		self.potcar = None

		save_path = self.get_save_path()

		file = open(save_path, 'w')
		file.write(cPickle.dumps(self.__dict__))
		file.close()

		self.potcar = stored_potcar

		self.log("Save successful")

	def load(self,load_path=None):

		self.log("Loading run")

		if not load_path:
			load_path = self.get_save_path()

		if not Path.exists(load_path):
			self.log("Load file path does not exist: " + load_path, raise_exception=True)

		file = open(load_path, 'r')
		data_pickle = file.read()
		file.close()

		self.__dict__ = cPickle.loads(data_pickle)

		#restore the full potcar from the basenames that were saved
		if self.potcar_minimal_form:
			self.potcar = Potcar(minimal_form=self.potcar_minimal_form)
			del self.potcar_minimal_form

		self.log("Load successful")

	def log(self, log_string, raise_exception=False):
		"""Tracks the output of the run, logging either to stdout or a local path file or both"""

		log_string = log_string.rstrip('\n') + '\n'

		if self.verbose:
			print log_string,

		log_string_with_time_stamp = su.get_time_stamp_string() + " || " + log_string

		if not Path.exists(VaspRun.log_path):
			File.touch(self.get_extended_path(VaspRun.log_path))

		log_file = File(self.get_extended_path(VaspRun.log_path))
		log_file.append(log_string_with_time_stamp)
		log_file.write_to_path()

		if raise_exception:
			raise Exception(log_string)

	def view(self, files_to_view=['Potcar', 'Kpoints', 'Incar', 'Poscar', 'Contcar', 'Submit.sh', '_JOB_OUTPUT.txt']):
		"""
		See printing of actual text input files written in directory, not internally stored input files.
		Useful for validating runs.

		files_to_view list is case insensitive - it will find 'POSCAR' file if you input 'poscar' for instance
		"""

		head_string = "==> "
		file_separator = 30*"-"
		output_string = ""
		output_string += "\n\n\n" + 30*"-" + "VaspRun View: Job ID is " + str(self.job_id_string) + 30*"-" + 40*"*" + "\n\n\n"
		output_string += head_string + "Path: " + self.path + "\n"

		for file_name in files_to_view:
			actual_file_name = Path.get_case_insensitive_file_name(self.path, file_name) #if Submit.sh is file_name, could find submit.sh for example

			if not actual_file_name:
				output_string += head_string + file_name + " file not present" + "\n"
				continue

			file_path = self.get_extended_path(actual_file_name)

			if actual_file_name.upper() == 'POTCAR':
				potcar = Potcar(file_path)
				file_string = " ".join(potcar.get_basenames_list())
			else:
				file = File(file_path)
				file_string = str(file)

			output_string += head_string + actual_file_name + ":\n" + file_separator + "\n" + file_string + file_separator + "\n\n"

		output_string += "\n\n" + 30*"-" + "End VaspRun View for Job ID " + str(self.job_id_string) + 30*"-" + "\n\n\n\n"

		print output_string,


	def __str__(self):
		head_string = "==> "
		file_separator = 30*"-"
		output_string = ""

		output_string += "\n" + 10*"-" + "VaspRun: Job ID is " + str(self.job_id_string) + 10*"-" + "\n"
		output_string += head_string + "Path: " + self.path + "\n"
		output_string += head_string + "Potcar: " + " ".join(self.potcar.get_titles()) + "\n"
		output_string += head_string + "Kpoints:\n" + file_separator + "\n" + str(self.kpoints) + file_separator + "\n"
		output_string += head_string + "Incar:\n" + file_separator + "\n" + str(self.incar) + file_separator + "\n"
		output_string += head_string + "Structure:\n" + file_separator + "\n" + str(self.structure) + file_separator + "\n"

		return output_string