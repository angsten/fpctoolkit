from collections import OrderedDict

from fpctoolkit.io.file import File

class Incar(File):

	separator_token = " = "

	def __init__(self, file_path=None):
		super(Incar, self).__init__(file_path)

		self.dict = OrderedDict()

		if file_path:
			pass #update dict here

	def __setitem__(self, key, value):
		key = key.rstrip()
		value = value.rstrip()

		self.dict[key] = value
		if not self.dict.has_key(key):
			self.lines.append(key + Incar.separator_token + value + '\n')
		else:
			pass
			#find line with this key and update the value

	def __getitem__(self, key):
		if self.dict.has_key(key):
			return self.dict[key]

	def __delitem__(self, key):
		del self.dict[key]
		#find line with this key and delete it