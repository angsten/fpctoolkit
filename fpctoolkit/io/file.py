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
	For a file with the first line containing '\n' and the second containing '', lines will contain [''] after loading.
	When writing or printing, a newline is always added.
	Many operators are overridden for convenience.

	Examples:
		file = File()
		file[2] = 'Can add in middle of file. Blanks lines will be added until this line.'
		file += 'New stuff' #appends line to end
		del file[3:5]
		print file[2:4]
		del file[2]
		file.insert(0,'at beginning now')
		new_file = some_file + another_file #concats files together

		file2 = File('some_path.txt')
		file2[6] = "write this line here"
		file2.write_to_path() #remembers the load path
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

	def __contains__(self, line_string):
		return bool(filter(lambda x: x.find(line_string) != -1, self))

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

	def insert(self, index, string=""): #index is item before which to insert
		self.lines.insert(index, string)


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

	def get_lines_containing_string(self, string):
		"""Return list of lines that contain string"""

		return filter(lambda x: x.find(string) != -1, self)

	def get_indices_of_lines_containing_string(self, string, modifier=None):
		"""Applies modifier to each line before searching"""
		indices = []
		new_lines = self.lines

		if modifier:
			new_lines = [modifier(line) for line in self]

		for i, line in enumerate(new_lines):
			if line.find(string) != -1:
				indices.append(i)

		return indices

	def trim_trailing_whitespace_only_lines(self):
		for i in range(len(self)-1, -1, -1):
			if self[i].strip() == "":
				del self[i]


	@staticmethod
	def concatenate(*files):
		concatenated_file = File()

		for file in files:
			file_copy = copy.deepcopy(file)
			concatenated_file.lines += file_copy.lines

		return concatenated_file

