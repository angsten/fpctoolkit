import copy

import fpctoolkit.util.string_util as su
from fpctoolkit.util.path import Path

class File(object):
	def __init__(self, file_path=None):
		self.lines = []
		self.load_path = None

		if file_path:
			self.load_from_path(file_path)

	def __str__(self):
		return "".join(self.lines)

	def __len__(self):
		return len(self.lines)

	def __add__(self, val): #self + val
		if val.__class__ == self.__class__: #if both files, create new file with lines added together
			return File.concatenate(self, val)
		else:
			return str(self) + str(val)

	def __radd__(self, val): #val + self
		if val.__class__ == self.__class__:
			return File.concatenate(val, self)
		else:
			return str(val) + str(self)

	def __getitem__(self, key):
		if isinstance(key, slice):
			return self.lines[key.start:key.stop]
		else:
			return self.lines[key]

	def __setitem__(self, key, value):
		if isinstance(key, slice):
			while len(self) < key.stop:
				self.append()
			self.lines[key.start:key.stop] = su.enforce_newline_on_list(value)
		else:
			while len(self) <= key:
				self.append()

			self.lines[key] = su.enforce_newline(value)

	def __delitem__(self, key):
		if isinstance(key, slice):
			del self.lines[key.start:key.stop]
		else:
			del self.lines[key]

	def __iter__(self):
		self.iter_index = -1
		return self

	def next(self):
		if self.iter_index >= (len(self.lines)-1):
			raise StopIteration
		self.iter_index += 1
		return self.lines[self.iter_index]

	def append(self, string=""):
		self.lines.append(su.enforce_newline(string))




	def load_from_path(self, file_path):
		self.load_path = file_path

		if Path.exists(file_path):
			with open(self.load_path, 'rb') as file:
				self.lines = file.readlines()
		File.standardize_newlines(self, '\n')

	def write_to_path(self, file_path=None):
		if not file_path:
			file_path = self.load_path

		with open(file_path, 'wb') as file:
			file.write(str(self))



	@staticmethod	
	def get_lines_containing_string(file, string):
		lines = []
		for line in file.lines:
			if not line.find(string) == -1:
				lines.append(line)
		return lines

	@staticmethod
	def standardize_newlines(file, newline_char):
		for line in file:
			line = line.replace('\r\n',newline_char)

	@staticmethod
	def pad_with_newline(file):
		if file.lines:
			file[-1] = file[-1].rstrip('\n') + '\n'
		return file

	@staticmethod
	def concatenate(*files):
		concatenated_file = File()
		for file in files:
			file_copy = File.pad_with_newline(copy.deepcopy(file))
			concatenated_file.lines += file_copy.lines

		return concatenated_file

