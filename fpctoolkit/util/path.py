import os
import shutil
from datetime import datetime

class Path(object):
	@staticmethod
	def expand_path(path):
		return os.path.abspath(os.path.expanduser(path))

	@staticmethod
	def join(*args):
		return Path.clean(*args)

	@staticmethod
	def clean(*paths):
		return Path.expand_path(os.path.join(*paths))

	@staticmethod
	def exists(path):
		return os.path.exists(path)

	@staticmethod
	def make(path):
		path = Path.clean(path)
		if not Path.exists(path):
			os.mkdir(path)

	@staticmethod
	def remove(path):
		path = Path.clean(path)

		if path == Path.clean("~"):
			raise Exception("Cannot remove entire home directory")

		if os.environ['QUEUE_ADAPTER_HOST'] == 'Tom_hp': #Don't want to destroy my home computer files
			if Path.exists(path):
				time = str(datetime.now()).replace('.', '_').replace(':', '_').replace('-', '_')
				move_path = Path.clean("C:\Users\Tom\Documents\Coding\python_work/fpc_recycle_bin/", os.path.basename(path)+'_'+time)
				shutil.move(path, move_path)
			return

		if Path.exists(path):
			if os.path.isfile(path):
				os.remove(path)
			elif os.path.isdir(path):
				shutil.rmtree(path)
