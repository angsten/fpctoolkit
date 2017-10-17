#from fpctoolkit.workflow.vasp_calculation import VaspCalculation

import time

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


class VaspCalculation(object):
	"""
	Class wrapper for vasp calculations. This class is meant to
	be as general as possible - it simply takes in a set of inputs,
	writes them out, and runs the calculation. There

	If wavecar_path, contcar_path, or chargecar_path is defined, will see if wavecar_path exists and copy the wavecar there 
	into the current run before beginning

	"""

	def __init__(self, path, initial_structure=None, incar=None, kpoints=None, potcar=None, submission_script_file=None, contcar_path=None, wavecar_path=None, chargecar_path=None):
		"""
		"""

		if initial_structure and contcar_path:
			raise Exception("Both an initial initial_structure and a contcar path is given. Only one is allowed.")

		self.path = Path.clean(path)
		self.initial_structure = initial_structure
		self.initial_incar = incar
		self.initial_kpoints = kpoints
		self.initial_potcar = potcar
		self.submission_script_file = submission_script_file
		self.contcar_path = contcar_path
		self.wavecar_path = wavecar_path
		self.chargecar_path = chargecar_path


	def update(self):
		"""Returns True if run is completed"""

		Path.make(self.path)

		#only if there is no job_id_string associated with this run should we start the run
		if not self.job_id_string:
			self.start()
			return False

		#check if run is complete
		if self.complete:
			print "Calculation at " + str(self.path) + ": complete"
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

		elif queue_status == QueueStatus.running:
			pass

			#use handler to check for run time errors here
		else:
			#Run is not active on queue ('C', 'E', or absent) but still isn't complete. An error must have occured. Use handler to check for errors here
			pass

		queue_properties_string = str(queue_properties) if queue_properties else 'Failed'
		print "Calculation at " + str(self.path) + ": " + queue_properties_string

		return False


	def start(self):
		"""Submit the calculation at self.path"""

		print "Starting calculation at " + self.path

		self.write_input_files_to_path()

		QueueAdapter.submit_job(self.path) #call auto saves id to .job_id in path

		if not self.job_id_string:
			raise Exception("Tried to start vasp run but an active job is already associated with its path.")

	def restart(self, even_if_running=True):
		"""Delete the job on queue, submit another job"""

		print "Resetting job at " + self.path

		was_reset = True

		if self.job_id_string != None:

			if (self.queue_properties['status'] != QueueStatus.running) or even_if_running:
				self.stop()
			else:
				was_reset = False

		if was_reset:
			time.sleep(0.5)

			QueueAdapter.submit_job(self.path)		
		
			if not self.job_id_string:
				raise Exception("Tried to start vasp run but an active job is already associated with its path.")


	def stop(self):
		"""If run has associated job on queue, delete this job"""
		
		QueueAdapter.terminate_job(self.job_id_string)

	def write_input_files_to_path(self):
		"""
		Simply write files to path
		"""

		if self.initial_structure:
			self.initial_structure.to_poscar_file_path(Path.clean(self.path, 'POSCAR'))
		elif not Path.exists(self.contcar_path):
			raise Exception("Neither an initial structure nor an existing contcar path have been provided. Nowhere to get the structure.")
		else:
			Path.copy(self.contcar_path, self.get_extended_path('POSCAR'))

		for file_path in [self.chargecar_path, self.wavecar_path]:
			if Path.exists(file_path):
				Path.copy(file_path, self.path)

		self.initial_incar.write_to_path(Path.join(self.path, 'INCAR'))

		if self.initial_kpoints: 
			self.initial_kpoints.write_to_path(Path.join(self.path, 'KPOINTS'))
		elif 'kspacing' not in self.incar:
			raise Exception("If no kpoints is provided, must have kspacing parameter in incar set")
			
		self.initial_potcar.write_to_path(Path.join(self.path, 'POTCAR'))
		self.submission_script_file.write_to_path(Path.join(self.path, 'submit.sh'))

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

	@property
	def job_id_string(self):
		"""Tracks job id associated with run on queue, looks like '35432'"""

		return QueueAdapter.get_job_id_at_path(self.path) #returns None if no .job_id file	

	@property
	def poscar(self):
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

	def get_final_structure(self):
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

	def get_final_forces_list(self):
		"""
		Returns list of forces - one for each x, y, z component of each atom, ordered by poscar position.
		"""

		if self.complete:
			return self.outcar.final_forces_list
		else:
			return None


	@property
	def total_time(self):
		"""Defaults to cpu*hours for now (best measure of total resources used)"""
		
		if self.complete:
			return self.outcar.get_calculation_time_in_core_hours()
		else:
			return None

	def delete_wavecar_if_complete(self):
		if Path.exists(self.get_extended_path('WAVECAR')) and self.complete:
			Path.remove(self.get_extended_path('WAVECAR'))

	def delete_big_vasp_files_if_complete(self):
		if self.complete:
			for file_name in ['WAVECAR', 'CHG', 'CHGCAR', 'vasprun.xml']:
				if Path.exists(self.get_extended_path(file_name)):
					Path.remove(self.get_extended_path(file_name))			

	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)





