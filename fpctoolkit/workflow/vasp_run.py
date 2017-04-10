#from fpctoolkit.workflow.vasp_run import VaspRun

import cPickle

from fpctoolkit.io.file import File
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.potcar import Potcar
from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.io.vasp.incar import Incar
from fpctoolkit.structure.structure import Structure
from fpctoolkit.io.vasp.outcar import Outcar
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

	If wavecar_path is defined, will see if wavecar_path exists and copy the wavecar there into the current run before beginning

	"""

	log_path = ".log"

	def __init__(self, path, structure=None, incar=None, kpoints=None, potcar=None, submission_script_file=None, input_set=None, custom_handler=None, wavecar_path=None, verbose=True):
		"""
		Cases for __init__:
		1. path does not exist or is empty => make the directory, enforce input file arguments all exists, write out input files to directory
		2. path exists and is not empty
			1. path/.job_id does not exist
				1. path has all 5 input files written to it already => do nothing if not all five input parameters exist, else overwrite current input files to directory
				2. path does not have all 5 input files (has some subset or none) => enforce input file arguments all exists, write out input files to directory
			2. path/.job_id exists => do nothing

		"""

		self.path = Path.clean(path)
		self.verbose = verbose

		if custom_handler:
			self.handler = custom_handler
		else:
			pass #self.handler = VaspHandler()

		if input_set:
			structure = input_set.structure
			incar = input_set.incar
			kpoints = input_set.kpoints
			potcar = input_set.potcar
			submission_script_file = input_set.submission_script_file

		all_essential_input_parameters_exist = not bool(filter(lambda x: x == None, [structure, incar, kpoints, potcar, submission_script_file]))

		if not Path.exists(self.path) or Path.is_empty(self.path):
			if not all_essential_input_parameters_exist:
				raise Exception("All five vasp input files must be input for run to be initialized.")
			else:
				Path.make(self.path)

				#self.log("Directory at run path did not exist or was empty. Created directory.")

				self.write_input_files_to_path(structure, incar, kpoints, potcar, submission_script_file, wavecar_path) 
		else:
			if self.job_id_string:
				pass
				#self.log("Non-empty directory has a job id associated with it.")
			else:
				#self.log("Non-empty directory does not have a job id associated with it.")
				if self.all_input_files_are_present(): #all input files are written to directory
					if all_essential_input_parameters_exist: #overwrite what's there
						#self.log("Overwriting existing complete input run files with new given input parameter files")
						self.write_input_files_to_path(structure, incar, kpoints, potcar, submission_script_file, wavecar_path)
					else:
						#self.log("Using existing run files at path")
						pass #do nothing - don't have the necessary inputs to start a run
				else: #not all input files currently exist - must have necessary input params to overwrite
					if not all_essential_input_parameters_exist:
						self.log("All five vasp input files must be input for run with incomplete inputs at path to be initialized.", raise_exception=True)
					else:
						#self.log("Overwriting existing partially-present run files with input parameter files")
						self.write_input_files_to_path(structure, incar, kpoints, potcar, submission_script_file, wavecar_path)
			
		

	def write_input_files_to_path(self, structure, incar, kpoints, potcar, submission_script_file, wavecar_path):
		"""
		Simply write files to path
		"""

		#self.log("Writing input files to path.")

		structure.to_poscar_file_path(Path.clean(self.path, 'POSCAR'))
		incar.write_to_path(Path.clean(self.path, 'INCAR'))
		kpoints.write_to_path(Path.clean(self.path, 'KPOINTS'))
		potcar.write_to_path(Path.clean(self.path, 'POTCAR'))
		submission_script_file.write_to_path(Path.clean(self.path, 'submit.sh'))

		if wavecar_path and Path.exists(wavecar_path):
			Path.copy(wavecar_path, self.get_extended_path('WAVECAR'))

	def all_input_files_are_present(self):
		"""Returns true if incar, poscar, potcar, kpoints, and submit script are all written out at path"""

		required_file_basenames_list = ['POSCAR', 'INCAR', 'KPOINTS', 'POTCAR', 'submit.sh']

		return Path.all_files_are_present(self.path, required_file_basenames_list)

	@property
	def job_id_string(self):
		"""Tracks job id associated with run on queue, looks like '35432'"""

		return QueueAdapter.get_job_id_at_path(self.path) #returns None if no .job_id file

	@property
	def initial_structure(self):
		if Path.exists(self.get_extended_path('./POSCAR')):
			return Structure(self.get_extended_path('./POSCAR'))
		else:
			return None

	@property
	def current_structure(self):
		if Path.exists(self.get_extended_path('./CONTCAR')):
			return Structure(self.get_extended_path('./CONTCAR'))
		else:
			return self.initial_structure

	@property
	def final_structure(self):
		if Path.exists(self.get_extended_path('./CONTCAR')) and self.complete:
			return Structure(self.get_extended_path('./CONTCAR'))
		else:
			return None

	@property
	def incar(self):
		incar_path = Path.clean(self.path, 'INCAR')
		if Path.exists(incar_path):
			return Incar(incar_path)
		else:
			return None

	@property
	def kpoints(self):
		kpoints_path = Path.clean(self.path, 'KPOINTS')
		if Path.exists(kpoints_path):
			return Kpoints(kpoints_path)
		else:
			return None

	@property
	def potcar(self):
		potcar_path = Path.clean(self.path, 'POTCAR')
		if Path.exists(potcar_path):
			return Potcar(potcar_path)
		else:
			return None

	@property
	def outcar(self):
		outcar_path = Path.clean(self.path, 'OUTCAR')
		if Path.exists(outcar_path):
			return Outcar(outcar_path)
		else:
			return None

	def get_final_energy(self, per_atom=True):
		if self.complete:
			if per_atom:
				return self.outcar.energy_per_atom
			else:
				return self.outcar.energy
		else:
			return None

	@property
	def total_time(self):
		"""Defaults to cpu*hours for now (best measure of total resources used)"""
		
		if self.complete:
			return self.outcar.get_calculation_time_in_core_hours()
		else:
			return None

	@property
	def complete(self):
		outcar = self.outcar

		if outcar:
			return outcar.complete
		else:
			return False

	@property
	def queue_properties(self):
		if not self.job_id_string:
			return None
		else:
			return QueueAdapter.get_job_properties_from_id_string(self.job_id_string)


	def update(self):
		"""Returns True if run is completed"""

		#only if there is not job_id_string associated with this run should we start the run
		if not self.job_id_string:
			#self.log("No job id stored in this run.")
			self.start()
			return False

		#check if run is complete
		if self.complete:
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
			pass
			#self.log("Job is on queue waiting.")

		elif queue_status == QueueStatus.running:
			pass
			#self.log("Job is on queue running. Queue properties: " + str(self.queue_properties))

			#use handler to check for run time errors here
		else:
			#self.log("Run is not active on queue ('C', 'E', or absent) but still isn't complete. An error must have occured.")
			pass
			#use handler to check for errors here

		return False

	def start(self):
		"""Submit the calculation at self.path"""

		#self.log("Submitting a new job to queue.")

		#Remove all output files here!!! Maybe store in hidden archived folder?####################
		self.archive_file('OUTCAR')

		QueueAdapter.submit_job(self.path) #call auto saves id to .job_id in path

		if not self.job_id_string:
			self.log("Tried to start vasp run but an active job is already associated with its path.", raise_exception=True)

	def stop(self):
		"""If run has associated job on queue, delete this job"""
		
		QueueAdapter.terminate_job(self.job_id_string)


	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)

	def get_save_path(self):
		return self.get_extended_path(".run_pickle")

	def get_archive_path(self):
		return self.get_extended_path(".run_archive")

	def archive_file(self, file_basename):
		"""
		Takes residual file (maybe from previous runs) and moves into self.path/.run_archive directory.
		Useful for making sure files like outcar are removed to somewhere before starting a new run -
		if this isn't done, could get false completes.
		"""

		file_path = self.get_extended_path(file_basename)
		archive_file_path = Path.join(self.get_archive_path(), file_basename + '_' + su.get_time_stamp_string())

		if Path.exists(file_path):
			if not Path.exists(self.get_archive_path()): #only make archive directory if at least one file will be in it
				Path.make(self.get_archive_path())

			Path.move(file_path, archive_file_path)

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
		output_string += "\n\n\n" + 30*"-" + "VaspRun View: Job ID is " + str(self.job_id_string) + 30*"-" + 55*"*" + "\n\n\n"
		output_string += head_string + "Path: " + self.path + "\n"

		for file_name in files_to_view:
			actual_file_name = Path.get_case_insensitive_file_name(self.path, file_name) #if Submit.sh is file_name, could find submit.sh for example

			if not actual_file_name:
				output_string += head_string + file_name + " file not present" + "\n"
				continue

			file_path = self.get_extended_path(actual_file_name)

			if actual_file_name.upper() == 'POTCAR':
				potcar = Potcar(file_path)
				file_string = " ".join(potcar.get_basenames_list()) + '\n'
			else:
				file = File(file_path)
				file_string = str(file)

			output_string += head_string + actual_file_name + ":\n" + file_separator + "\n" + file_string + file_separator + "\n\n"

		output_string += "\n\n" + 30*"-" + "End VaspRun View for Job ID " + str(self.job_id_string) + 30*"-" + "\n\n\n\n"

		print output_string,


	# def __str__(self):
	# 	head_string = "==> "
	# 	file_separator = 30*"-"
	# 	output_string = ""

	# 	output_string += "\n" + 10*"-" + "VaspRun: Job ID is " + str(self.job_id_string) + 10*"-" + "\n"
	# 	output_string += head_string + "Path: " + self.path + "\n"
	# 	output_string += head_string + "Potcar: " + " ".join(self.potcar.get_titles()) + "\n"
	# 	output_string += head_string + "Kpoints:\n" + file_separator + "\n" + str(self.kpoints) + file_separator + "\n"
	# 	output_string += head_string + "Incar:\n" + file_separator + "\n" + str(self.incar) + file_separator + "\n"
	# 	output_string += head_string + "Structure:\n" + file_separator + "\n" + str(self.structure) + file_separator + "\n"

	# 	return output_string