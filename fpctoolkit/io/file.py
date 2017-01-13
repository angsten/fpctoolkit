



class File(object):
	def __init__(self, file_path=None):
		self.lines = []
		self.load_path = None

		if file_path:
			self.load_from_path(file_path)

	def __str__(self):
		return "".join(self.lines)

	def __add__(self, val):
		return str(self) + str(val)

	def __getitem__(self, key):
		if isinstance(key,slice):
			return self.lines[key.start:key.stop]
		else:
			return self.lines[key]

	def __setitem__(self, key, value):
		if isinstance(key,slice):
			self.lines[key.start:key.stop] = value
		else:
			self.lines[key] = value

	def __delitem__(self, key):
		if isinstance(key,slice):
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


	def load_from_path(self, file_path):
		self.load_path = file_path
		with open(self.load_path, 'rb') as file:
			self.lines = file.readlines()

	def write_to_path(self, file_path=None):
		if not file_path:
			file_path = self.load_path

		with open(file_path,'wb') as file:
			file.write(str(self))





