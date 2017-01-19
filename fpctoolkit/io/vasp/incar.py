from collections import OrderedDict

from fpctoolkit.io.file import File

class Incar(File):
	"""Multiple parameters assigned in one line not supported

	"""

	output_separator_token = " = "

	def __init__(self, file_path=None):
		super(Incar, self).__init__(file_path)

		if file_path: #update dict here from loaded file text lines
			self.update_dictionary_from_file_lines()


	def __setitem__(self, key, value):
		if not isinstance(key, basestring): #treat as file line index setter
			super(Incar, self).__setitem__(key, value)
			self.update_dictionary_from_file_lines()
		else: #key must be a dictionary key of type string
			if not self.dict.has_key(key):
				self += Incar.get_line_string(key, value)
			else: #find actual line with this key and update the value
				line_index_list = self.get_indices_of_lines_containing_string(key, Incar.get_line_with_comments_removed)
				if len(line_index_list) > 1:
					raise Exception("Key " + key + " found in incar file multiple times")

				line_index = line_index_list[0]

				self[line_index] = Incar.get_line_string(key, value)
			
			self.dict[key.strip()] = str(value).strip()

	def __getitem__(self, key):
		if not isinstance(key, basestring): #treat as file line index getter
			return super(Incar, self).__getitem__(key)
		else:
			if self.dict.has_key(key):
				return self.dict[key]

	def __delitem__(self, key):
		if not isinstance(key, basestring):
			super(Incar, self).__delitem__(key)
		else:
			del self.dict[key]
			#find line with this key and delete it##############################

	def __contains__(self, key):
		if not isinstance(key, basestring):
			return super(Incar, self).__contains__(key)
		else:
			return (key in self.dict)

	def update_dictionary_from_file_lines(self):
		self.dict = OrderedDict()
		for (key, value) in self.get_valid_key_value_pairs_from_file_lines():
			if key in self:
				raise Exception("Incar file lines contain key " + key + " twice.")
			else:
				self[key] = value

	def get_valid_key_value_pairs_from_file_lines(self):
		"""Get key value pairs for lines with valid separator char in it ('=').
			This method will not find multiple key value pairs in one line.
			Commented character not included.
		"""
		key_value_pairs = []

		for parameter_line_string in self.parameter_line_strings_list:
			if parameter_line_string:
				Incar.validate_incar_parameter_line(parameter_line_string)
				key_value_pairs.append( (param.strip() for param in parameter_line_string.split("=")) )

		return key_value_pairs

	@property
	def parameter_line_strings_list(self):
		#gives all lines with comments stripped which contain '=' character
		return [Incar.get_line_with_comments_removed(line) for line in self.get_lines_containing_string("=")]

	@staticmethod
	def get_line_with_comments_removed(line_string):
		return line_string.split('#')[0] #cut off to right of comments

	@staticmethod
	def validate_incar_parameter_line(parameter_line_string):
		if parameter_line_string.count('=') != 1:
			raise Exception("Must have exactly one key value pair in one incar parameter line.")

	@staticmethod
	def get_line_string(key, value):
		return key.strip() + Incar.output_separator_token + value.strip()