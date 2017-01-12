

from fpctoolkit.util.path import Path

class File(object):
	def __init__(self, file_path=None):
		self.data = []
		self.load_path = ""

		if file_path:
			self.load_from_path(file_path)

	def __str__(self):
		return "".join(self.data)

	def __add__(self,val):
		return str(self) + str(val)

	def __getitem__(self,key):
		if isinstance(key,slice):
			return self.data[key.start:key.stop]
		else:
			return self.data[key]

	def __setitem__(self,key,value):
		if isinstance(key,slice):
			self.data[key.start:key.stop] = value
		else:
			self.data[key] = value

	def __delitem__(self,key):
		if isinstance(key,slice):
			del self.data[key.start:key.stop]
		else:
			del self.data[key]

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
		with open(self.load_path, 'rb') as file:
			self.data = file.readlines()

	def write_to_path(self, file_path=None):
		if not file_path:
			file_path = self.load_path
		else:
			file_path = Path.clean_path(file_path)
		with open(file_path,'wb') as file:
			file.write(str(self))




