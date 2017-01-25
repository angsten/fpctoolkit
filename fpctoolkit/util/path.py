import os
import shutil

class Path(object):
	@staticmethod
	def expand_path(path):
		return os.path.abspath(os.path.expanduser(path))

	@staticmethod
	def join(*args):
		return os.path.join(*args)

	@staticmethod
	def clean(*paths):
		return Path.expand_path(Path.join(*paths))

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

		if Path.exists(path):
			if os.path.isfile(path):
				os.remove(path)
			elif os.path.isdir(path):
				shutil.rmtree(path)
