import copy

#import fpctoolkit.util.string_util as su
from fpctoolkit.util.path import Path

class File(object):
	"""
	A file is a container of strings. These strings correspond to the lines of 
	loaded text file and are stored in the lines attribute. Stored strings in 
	the lines list lack an end-of-line character (\n or \r\n) at the end - this is added 
	by other functions upon printing the file.
	Lines, in files, that have neither content nor an eol character are not added to the list of lines.
	Thus, for an empty file, lines will be the empty list, [].
	For a file with the first line containing '\n' and the second '', lines will have [''] after loading.
	When writing or printing, a newline is always added.

	Cool examples:
	file = File()
	file[2] = 'Can add in middle of file. Blanks lines will be added until this line.'
	file[3:5] = ['this','is','a sequence']
	"""
	def __init__(self, file_path=None):
		self.lines = []
		self.load_path = None

		if file_path:
			self.load_from_path(file_path)


	def __str__(self):
		return "\n".join(self.lines) + "\n" if self else "" #always add \n unless empty file or last line is newline

	def __nonzero__(self):
		return bool(self.lines)

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


	def __iadd__(self, val):
		self.append(val)
		return self


	def __getitem__(self, key):
		if isinstance(key, slice):
			return self.lines[key.start:key.stop]
		else:
			return self.lines[key]


	def __setitem__(self, key, value):
		if isinstance(key, slice):
			raise AttributeError("Cannot set items with slices.")
			# while len(self) < key.stop:
			# 	self.append()

			# self.lines[key.start:key.stop] = [v.rstrip('\r\n') for v in value]
		else:
			while len(self) < key:
				self.append()

			self.lines[key:key+1] = (value.rstrip('\r\n')).split('\n')


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
		string = string.rstrip('\r\n')
		strings = string.split('\n')
		self.lines += strings


	def load_from_path(self, file_path):
		if Path.exists(file_path):
			self.load_path = file_path

			with open(self.load_path, 'rb') as file:
				self.lines = [line.rstrip('\r\n') for line in file.readlines()]

		else:
			raise IOError('File does not exist at path ' + file_path)


	def write_to_path(self, file_path=None):
		if not file_path:
			if self.load_path:
				file_path = self.load_path
			else:
				raise IOError('File write path not defined')

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
	def concatenate(*files):
		concatenated_file = File()

		for file in files:
			file_copy = copy.deepcopy(file)
			concatenated_file.lines += file_copy.lines

		return concatenated_file

