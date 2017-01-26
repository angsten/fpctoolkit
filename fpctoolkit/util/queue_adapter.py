import os
import subprocess

from fpctoolkit.io.file import File
from fpctoolkit.util.path import Path
import fpctoolkit.util.string_util as su

class QueueAdapter(object):
	host = os.environ['QUEUE_ADAPTER_HOST']
	user = os.environ['USER']
	id_path = ".job_id" #where id's are saved upon submission
	error_path = "QUEUE_SUBMISSION_ERROR_OUTPUT"

	@staticmethod
	def submit_job(calculation_path, override=False):
		"""This safely submits jobs and records the associated id at calculation_path/.job_id

		If an id exists in this file, it is first checked that it is not active on the queue.
		If it is active, the override parameter determines whether or not to cancel that job
		and submit the current one (thus overwriting the .job_id file).
		
		For safety, qsub should be aliased to execute this code on every machine.
		"""

		id = None
		submit = True

		if submit:
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

		return id

	@staticmethod
	def get_job_id_at_path(calculation_path):
		"""Looks in the .job_id file for an id. Returns id as a string if present, None if not present"""

		id_path = Path.join(calculation_path, QueueAdapter.id_path)

		if Path.exists(id_path):
			return File(id_path)[0]
		else:
			return None

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
	def get_job_status_at_path(calculation_path):
		"""Finds id in calculation_path/.job_id (or lack thereof) and
		returns status. possible statuses are denoted in the QueueStatus
		class below
		"""

		if QueueAdapter.host == 'Fenrir':
			pass
		elif QueueAdapter.host == 'Tom_hp':
			pass
		else:
			raise Exception("QueueAdapter.host not supported")

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

		elif QueueAdapter.host == 'Tom_hp':
			pass
		else:
			raise Exception("QueueAdapter.host not supported")

		return output_file

	@staticmethod
	def get_job_properties_from_id_string(id_string):
		"""Takes in id_string like '32223' and return dictionary of run properties that looks like:
		{'status': QueueStatus.off_queue} or {'status': QueueStatus.running, 'node_count': 1, 'wall_time_limit': '16:00', 'elapsed_time': '00:08'}

		Possible statuses are denoted in the QueueStatus class below.
		"""
		output_dictionary = {'status': QueueStatus.off_queue}
		if QueueAdapter.host == 'Fenrir':
			queue_view_file = QueueAdapter.get_queue_view_file()

			lines = queue_view_file.get_lines_containing_string(id_string + '.fenrir.bw')

			if len(lines) > 1:
				raise Exception("Multiple entries in queue view for same id found.")

			if lines:
				queue_line = lines[0] #looks like '682554.fenrir.bw     angsten  default  job               16794     1  --    --  16:00 R 00:01'
				queue_line = su.remove_extra_spaces(queue_line) #'682554.fenrir.bw angsten default job 16794 1 -- -- 16:00 R 00:01'
				node_count = queue_line.split(' ')[5]
				wall_time_limit = queue_line.split(' ')[8]
				run_code = queue_line.split(' ')[9]
				elapsed_time = queue_line.split(' ')[10]

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
	def _template():
		if QueueAdapter.host == 'Fenrir':
			pass
		elif QueueAdapter.host == 'Tom_hp':
			pass
		else:
			raise Exception("QueueAdapter.host not supported")

	@staticmethod
	def _template():
		if QueueAdapter.host == 'Fenrir':
			pass
		elif QueueAdapter.host == 'Tom_hp':
			pass
		else:
			raise Exception("QueueAdapter.host not supported")


	#submits submit.sh to queue in calculation_path
	#if override, will remove job attached to calculation_path directory from queue and submit a new job
	#returns true if job is submitted
	@staticmethod
	def submitRun(calculation_path, override = False):
	    submit = False
	    id_path = os.path.join(calculation_path,'.id')

	    status = getJobStatus(calculation_path)
	    if status == 'NO_ID' or status == 'OFF_QUEUE': #submit in this case no matter what - no job for this path is waiting or running on queue
	        submit = True
	    elif status == 'ON_QUEUE' and override: #then delete the current run on queue and resubmit
	        terminateJob(calculation_path)
	        submit = True

	    if submit: #submit job to queue at this directory using submit.sh and write id to .id
	        cwd = os.getcwd()
	        os.chdir(calculation_path)

	        time.sleep(0.1) #sleeping can help success of submission
	        process = subprocess.Popen(["qsub","submit.sh"], stdout=subprocess.PIPE)
	        out,err = process.communicate() #get output from qsub command
	        id = out.split('.')[0] #get the job id portion of 45643.fenerir...etc
	        time.sleep(0.1)

	        wfile = open(id_path,'wb')
	        wfile.write(id+'\n')
	        wfile.close()

	        os.chdir(cwd)

	    return submit


	@staticmethod
	def get_submission_file():
		if QueueAdapter.host == 'Fenrir':
			return File(Path.clean("/home/angsten/.submit.sh"))

		elif QueueAdapter.host == 'Tom_hp':
			return File()

	@staticmethod
	def modify_number_of_cores_from_num_atoms(submission_file, num_atoms):
		"""Each system should specify how many cores to use based
		on the size of a calculation"""

		return submission_file

	@staticmethod
	def get_optimal_npar(submission_file):
		if QueueAdapter.host == 'Fenrir':
			return 2 #this is almost always the best choice on fenrir
		elif QueueAdapter.host == 'Tom_hp':
			return 1


class QueueStatus(object):
	off_queue = 1
	queued = 2 #i.e., has 'Q' as status
	running = 3 #'R'
	complete = 4 #'C'
	errored = 5