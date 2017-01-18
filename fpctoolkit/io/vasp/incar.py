from collections import OrderedDict

from fpctoolkit.io.file import File

class Incar(File):

	output_separator_token = " = "

	def __init__(self, file_path=None):
		super(Incar, self).__init__(file_path)

		self.dict = OrderedDict()

		if file_path: #update dict here

			for (key, value) in self.get_valid_key_value_pairs_from_file():
				self[key] = value

	def __setitem__(self, key, value):
		if not isinstance(key, basestring): #treat as file line index setter
			super(Incar, self).__setitem__(key, value)
		else:
			key = key.rstrip()
			value = value.rstrip()
			self.dict[key] = value

			if not self.dict.has_key(key):
				self += key + Incar.output_separator_token + value
			else: #find actual line with this key and update the value
				for index, (old_key, value) in enumerate(self.get_valid_key_value_pairs_from_file()):
					if key == old_key:
						self[index] = key + Incar.output_separator_token + value #gets wrong line number set
				

	def __getitem__(self, key):
		if not isinstance(key, basestring): #treat as file line index getter
			super(Incar, self).__getitem__(key)
		else:
			if self.dict.has_key(key):
				return self.dict[key]

	def __delitem__(self, key):
		del self.dict[key]
		#find line with this key and delete it


	def get_valid_key_value_pairs_from_file(self):
		"""Get key value pairs for lines with valid separator in it"""
		key_value_pairs = []
		parameter_strings_list = self.get_lines_containing_string("=")

		for parameter_string in parameter_strings_list:
			key_value_pairs.append( (param.strip() for param in parameter_string.split("=")) )

		return key_value_pairs