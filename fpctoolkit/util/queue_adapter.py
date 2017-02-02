import os
import subprocess
import time

from fpctoolkit.io.file import File
from fpctoolkit.util.path import Path
import fpctoolkit.util.string_util as su

class QueueAdapter(object):
	host = os.environ['QUEUE_ADAPTER_HOST']
	user = 'angsten'#os.environ['USER']######################################!!!!!!!!!!!!!!!!!!!!!!!!##############
	id_path = ".job_id" #where id's are saved upon submission
	error_path = "QUEUE_SUBMISSION_ERROR_OUTPUT"

	sleep_buffer_time = 0.2 #good idea to add in some buffer (in seconds) between deletions and submissions of jobs

	@staticmethod
	def submit_job(calculation_path, override_existing_job=False):
		"""This safely submits jobs and records the associated id at calculation_path/.job_id

		If an id exists in this file, it is first checked that it is not active on the queue.
		If it is active ('R' or 'Q' status), the override_existing_job parameter determines whether or not to cancel that job
		and submit the current one (thus overwriting the .job_id file).

		The id_string of the submitted job is returned (looks like "33254") if a submission is done, else None
		
		For safety, qsub should be aliased to execute this code on every machine.
		"""

		previous_id_string = QueueAdapter.get_job_id_at_path(calculation_path) #returns None if no id

		if QueueAdapter.job_id_is_active(previous_id_string):
			if not override_existing_job:
				return None #previous id is active, don't want to override - no new job id
			else:
				QueueAdapter.terminate_job(previous_id_string)
				time.sleep(QueueAdapter.sleep_buffer_time)


		if QueueAdapter.host == 'Fenrir':
			cwd = os.getcwd()
			os.chdir(calculation_path)

			#This call pipes through output and error which can be obtained from communicate() call
			process = subprocess.Popen(["qsub", "submit.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			output, error = process.communicate() #get output and error from the qsub command

			if error: #error will be None if no error is caused
				QueueAdapter.write_error_to_path(calculation_path, error)
				raise Exception("Error in submitting job to path " + calculation_path + " See error file at this path for details.")
			else:
				id_string = output.split('.')[0] #get the job id portion of 45643.fenerir...etc
				QueueAdapter.write_id_string_to_path(calculation_path, id_string)

			time.sleep(QueueAdapter.sleep_buffer_time)

			os.chdir(cwd)

		elif QueueAdapter.host == 'Tom_hp':
			cwd = os.getcwd()
			os.chdir(calculation_path)
			print "Fake run submission"
			id_string = '1'
			QueueAdapter.write_id_string_to_path(calculation_path, id_string)
			os.chdir(cwd)
			
		else:
			raise Exception("QueueAdapter.host not supported")

		return id_string

	@staticmethod
	def terminate_job(id_string):
		"""Terminates job with id id_string only if this job is active on queue"""

		if self.job_id_is_active(id_string):
			process = subprocess.Popen(['qdel', id_string], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			output, error = process.communicate()

			if error:
				raise Exception("Failure deleting active job with id: " + id_string)


	@staticmethod
	def get_job_id_at_path(calculation_path):
		"""Looks in the .job_id file for an id. Returns id as a string if present, None if not present"""

		id_path = Path.join(calculation_path, QueueAdapter.id_path)

		if Path.exists(id_path):
			return File(id_path)[0]
		else:
			return None

	@staticmethod
	def job_id_is_active(id_string):
		"""Returns true if job id is on the queue with queued or running status ('Q' or 'R')"""

		if not id_string: #if it's none, return false
			return False

		if QueueAdapter.host == 'Fenrir':
			job_properties = QueueAdapter.get_job_properties_from_id_string(id_string)

			if not job_properties: #job does not show up on queue at all
				return False

			status = job_properties['status']

			return QueueStatus.is_status_active(status)

		elif QueueAdapter.host == 'Tom_hp':
			pass
		else:
			raise Exception("QueueAdapter.host not supported")


	@staticmethod
	def write_id_string_to_path(calculation_path, id_string):
		"""Writes id_string to the first line of the id file at id_path"""

		id_path = Path.join(calculation_path, QueueAdapter.id_path)
		file = File()
		file[0] = id_string
		file.write_to_path(id_path)

	@staticmethod
	def write_error_to_path(calculation_path, error_string):
		error_path = Path.join(calculation_path, QueueAdapter.error_path + "_" + su.get_time_stamp_string())
		file = File()
		file[0] = error_string
		file.write_to_path(error_path)

	@staticmethod
	def get_job_properties_from_id_string(id_string):
		"""Takes in id_string like '32223' and return dictionary of run properties of the job"""

		job_property_dictionary = QueueAdapter.get_job_property_dictionary()

		if id_string in job_property_dictionary:
			return job_property_dictionary[id_string]
		else:
			return None

	@staticmethod
	def get_job_properties_from_queue_view_line(line_string):
		"""
		Takes in string that looks like '682554.fenrir.bw     angsten  default  job               16794     1  --    --  16:00 R 00:01'
		and returns property set like 
		{'status': QueueStatus.off_queue} or 
		{'status': QueueStatus.running, 'node_count': 1, 'wall_time_limit': '16:00', 'elapsed_time': '00:01'}

		Possible statuses are denoted in the QueueStatus class below.
		"""
		output_dictionary = {}

		if QueueAdapter.host == 'Fenrir':
			line_string = su.remove_extra_spaces(line_string) #'682554.fenrir.bw angsten default job 16794 1 -- -- 16:00 R 00:01'
			node_count = line_string.split(' ')[5]
			wall_time_limit = line_string.split(' ')[8]
			run_code = line_string.split(' ')[9]
			elapsed_time = line_string.split(' ')[10]

			if run_code == 'Q':
				status = QueueStatus.queued
			elif run_code == 'R':
				status = QueueStatus.running
			elif run_code == 'C':
				status = QueueStatus.complete
			elif run_code == 'E':
				status = QueueStatus.errored
			else:
				raise Exception("Could not identify queue status: " + run_code)

			output_dictionary = {'status':status, 'node_count':node_count, 'wall_time_limit':wall_time_limit,'elapsed_time':elapsed_time}

		elif QueueAdapter.host == 'Tom_hp':
			pass
		else:
			raise Exception("QueueAdapter.host not supported")

		return output_dictionary

	@staticmethod
	def get_queue_view_file():
		"""Returns a file that gives information of all jobs for this user. Looks something like like:

		682554.fenrir.bw     angsten  default  job               16794     1  --    --  16:00 R 00:01
		682555.fenrir.bw     angsten  default  job               16794     1  --    --  16:00 R 00:01
		682557.fenrir.bw     angsten  default  job               16794     1  --    --  16:00 C 00:03
		"""
		output_file = File()

		if QueueAdapter.host == 'Fenrir':
			queue_view_process = subprocess.Popen("qstat -a | grep " + QueueAdapter.user, shell=True, stdout=subprocess.PIPE)
			output, error = queue_view_process.communicate()

			if error:
				raise Exception("Error in getting view of queue: " + error)
			else:
				output_file += output #output is string with \n's built in - file class will handle this automatically
				output_file.trim_trailing_whitespace_only_lines() #otherwise empty output will lead to lines in out_file looking like [''] - errors out then

		elif QueueAdapter.host == 'Tom_hp':
			pass
		else:
			raise Exception("QueueAdapter.host not supported")

		return output_file

	@staticmethod
	def get_job_property_dictionary():
		"""returns a dictionary of all job property dictionaries for jobs showing up on the queue that looks like:
			
		{'46442':{'status': QueueStatus.running, 'node_count': 1, 'wall_time_limit': '16:00', 'elapsed_time': '00:01'}, '3324':...etc}
		"""

		job_property_dictionary = {}
		if QueueAdapter.host == 'Fenrir':
			queue_view_file = QueueAdapter.get_queue_view_file()

			for queue_line in queue_view_file:
				job_id_string = queue_line.split('.')[0]
				job_properties = QueueAdapter.get_job_properties_from_queue_view_line(queue_line)

				if job_id_string in job_property_dictionary:
					raise Exception("Multiple entries in queue view for same id found.")
				else:
					job_property_dictionary[job_id_string] = job_properties

		elif QueueAdapter.host == 'Tom_hp':
			pass
		else:
			raise Exception("QueueAdapter.host not supported")

		return job_property_dictionary

	@staticmethod
	def get_queue_count():
		"""Returns count of jobs either queued 'Q' or running 'R'"""

		active_job_count = 0

		job_property_dictionary = QueueAdapter.get_job_property_dictionary()

		for job_id_string, job_properties in job_property_dictionary.items():
			if QueueStatus.is_status_active(job_properties['status']):
				active_job_count += 1

		return active_job_count

	@staticmethod
	def _template():
		if QueueAdapter.host == 'Fenrir':
			pass
		elif QueueAdapter.host == 'Tom_hp':
			pass
		else:
			raise Exception("QueueAdapter.host not supported")


	@staticmethod
	def get_submission_file():
		if QueueAdapter.host == 'Fenrir':
			return File(Path.clean("/home/angsten/.submit.sh"))

		elif QueueAdapter.host == 'Tom_hp':
			return File()

	@staticmethod
	def modify_number_of_cores_from_num_atoms(submission_file, num_atoms):
		"""
		Each system should specify how many cores to use based
		on the size of a calculation
		"""

		if QueueAdapter.host == 'Fenrir':
			node_count = 1
			if num_atoms >= 40:
				node_count = 2
			if num_atoms >= 80:
				node_count = 4
			if num_atoms >= 160:
				node_count = 8

			node_count_line_indices = submission_file.get_line_indices_containing_string("#PBS -l nodes=")

			if len(node_count_line_indices) != 1:
				raise Exception("Could not find node count line (or there are multiple) in submission file")
				
			submission_file[node_count_line_indices[0]] = "#PBS -l nodes=" + str(node_count) + ":ppn=8:node"
		elif QueueAdapter.host == 'Tom_hp':
			pass
		else:
			raise Exception("QueueAdapter.host not supported")

		return submission_file

	@staticmethod
	def get_optimal_npar(submission_file):
		if QueueAdapter.host == 'Fenrir':
			return 2 #this is almost always the best choice on fenrir
		elif QueueAdapter.host == 'Tom_hp':
			return 1
		else:
			raise Exception("QueueAdapter.host not supported")

	@staticmethod
	def modify_submission_script(submission_file, modification_key, gamma=False):
		"""
		Modifies submission_file based on the given modification_key. Keys could include:
		'100', '' with gamma = True, '100', 'standard',...etc. Any with gamma = True okay too
		"""

		if QueueAdapter.host == 'Fenrir':
			program_line_indices = submission_file.get_line_indices_containing_string("MYMPIPROG=")

			if len(program_line_indices) != 1:
				raise Exception("Could not find mpiprog line in submission script (or found multiple lines)")

			if modification_key == 'standard':
				submission_file[program_line_indices[0]] = 'MYMPIPROG="${HOME}/bin/vasp_5.4.1_standard"'
			elif modification_key == '100':
				submission_file[program_line_indices[0]] = 'MYMPIPROG="${HOME}/bin/vasp_5.4.1_100_constrained"'

		elif QueueAdapter.host == 'Tom_hp':
			return 1
		else:
			raise Exception("QueueAdapter.host not supported")

		return submission_file

	# file = open(script_path,'rb')
	# lines = file.readlines()
	# file.close()

	# file = open(script_path,'wb')
	# for l in lines:
	# 	if not l.find("MYMPIPROG=") == -1:
	# 		if modified_version == '100': #use recompiled vasp in submission script
	# 			if gamma:
	# 				file.write('MYMPIPROG="${HOME}/bin/vasp_5.4.1_100_constrained_gamma"\n')
	# 			else:
	# 				file.write('MYMPIPROG="${HOME}/bin/vasp_5.4.1_100_constrained"\n')
	# 		elif modified_version == '110':
	# 			file.write('MYMPIPROG="${HOME}/vasp_mod/modified_110_vasp.5.4.1/bin/vasp_std"\n')
	# 		elif modified_version == '111':
	# 			file.write('MYMPIPROG="${HOME}/vasp_mod/modified_111_vasp.5.4.1/bin/vasp_std"\n')
	# 		elif modified_version == 'standard':
	# 			if gamma:
	# 				file.write('MYMPIPROG="${HOME}/bin/vasp_5.4.1_gamma"\n')
	# 			else:
	# 				file.write('MYMPIPROG="${HOME}/bin/vasp_5.4.1_standard"\n')
	# 	else:
	# 		file.write(l)



class QueueStatus(object):
	off_queue = 1
	queued = 2 #i.e., has 'Q' as status
	running = 3 #'R'
	complete = 4 #'C'
	errored = 5

	@staticmethod
	def is_status_active(queue_status):
		return queue_status in [QueueStatus.queued, QueueStatus.running]