import os

from fpctoolkit.util.path import Path

class File(object):
	def __init__(self, file_path=None):
		self.data = []
		self.load_path = ""

		if file_path:
			self.load_from_path(file_path)

	def __iter__(self):
		self.iter_index = -1
		return self

	def next(self):
		if self.iter_index >= (len(self.data)-1):
			raise StopIteration
		self.iter_index += 1
		return self.data[self.iter_index]

	def load_from_path(self, file_path):
		self.load_path = Path.clean_path(file_path)
		self.data = open(self.load_path, 'rb').readlines()

	def write_to_path(self, file_path):
		

	def __str__(self):
		return "".join(self.data)

