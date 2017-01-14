import os

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