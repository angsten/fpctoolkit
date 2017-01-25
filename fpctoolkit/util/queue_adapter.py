import os

from fpctoolkit.io.file import File
from fpctoolkit.util.path import Path

class QueueAdapter(object):
	host = os.environ['QUEUE_ADAPTER_HOST']

	@staticmethod
	def submit(calculation_path, override=False):
		id = None
		submit = True

		if submit:
			if QueueAdapter.host == 'Fenrir':
				cwd = os.getcwd()

				os.chdir(calculation_path)

				process = subprocess.Popen(["qsub", "submit.sh"], stdout=subprocess.PIPE)
				out, err = process.communicate() #get output from qsub command
				id = out.split('.')[0] #get the job id portion of 45643.fenerir...etc

				os.chdir(cwd)

			elif QueueAdapter.host == 'Tom_hp':
				cwd = os.getcwd()
				os.chdir(calculation_path)
				print "Fake run submission"
				os.chdir(cwd)
				id = 1

		return id

	#submits submit.sh to queue in calculation_path
	#if override, will remove job attached to calculation_path directory from queue and submit a new job
	#returns true if job is submitted
	@staticmethod
	def submitRun(calculation_path,override = False):
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