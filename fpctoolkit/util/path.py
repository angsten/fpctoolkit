import os

class Path(object):

	def __init__(self,path):
		self.path = path

	@staticmethod
	def clean_path(path):
		return os.path.expanduser(os.path.abspath(path))

	@property
	def path(self):
		return self._path

	@path.setter
	def path(self,path):
		self._path = os.path.expanduser(os.path.abspath(path))

	def __str__(self):
		return self.path