from collections import OrderedDict

from fpctoolkit.io.file import File

class Incar(File):
	"""Multiple parameters assigned in one line not supported

	"""

	output_separator_token = " = "

	def __init__(self, file_path=None):
		super(Incar, self).__init__(file_path)

		self.trim_trailing_whitespace_only_lines()

		if file_path: #update dict here from loaded file text lines
			self.update_dictionary_from_file_lines()


	def __setitem__(self, key, value):
		if not isinstance(key, basestring): #treat as file line index setter
			super(Incar, self).__setitem__(key, value)
			self.update_dictionary_from_file_lines()
		else: #key must be a dictionary key of type string
			key = Incar.get_processed_key_string(key)

			if key not in self:
				self += Incar.get_line_string(key, value)
			else: #find actual line with this key and update the value
				line_index_list = self.get_indices_of_lines_containing_string(key, Incar.get_line_with_comments_removed)
				if len(line_index_list) > 1:
					raise Exception("Incar file contains " + key + " key twice.")

				line_index = line_index_list[0]

				self[line_index] = Incar.get_line_string(key, value)
			
			self.assign_key_value_pair(key, value)

	def __getitem__(self, key):
		if not isinstance(key, basestring): #treat as file line index getter
			return super(Incar, self).__getitem__(key)
		else:
			key = Incar.get_processed_key_string(key)
			if key in self:
				return self.dict[key]

	def __delitem__(self, key):
		if not isinstance(key, basestring):
			super(Incar, self).__delitem__(key)
		else:
			key = Incar.get_processed_key_string(key)
			del self.dict[key]
			#find line with this key and delete it##############################

	def __contains__(self, key):
		if not isinstance(key, basestring):
			return super(Incar, self).__contains__(key)
		else:
			key = Incar.get_processed_key_string(key)
			return (key in self.dict)

	def update_dictionary_from_file_lines(self):
		self.dict = OrderedDict()
		for (key, value) in self.get_valid_key_value_pairs_from_file_lines():
			if Incar.get_processed_key_string(key) in self:
				raise Exception("Incar file contains key " + Incar.get_processed_key_string(key) + " twice.")
			else:
				self.assign_key_value_pair(key, value)

	def get_valid_key_value_pairs_from_file_lines(self):
		"""Get key value pairs for lines with valid separator char in it ('=').
			This method will not find multiple key value pairs in one line.
			Commented character not included.
		"""
		key_value_pairs = []

		for parameter_line_string in self.parameter_line_strings_list:
			if parameter_line_string:
				Incar.validate_incar_parameter_line(parameter_line_string)
				key_value_pairs.append(parameter_line_string.split("="))

		return key_value_pairs

	@property
	def parameter_line_strings_list(self):
		#gives all lines with comments stripped which contain '=' character
		return [Incar.get_line_with_comments_removed(line) for line in self.get_lines_containing_string("=")]

	def assign_key_value_pair(self, key, value):
		self.dict[Incar.get_processed_key_string(key)] = Incar.get_processed_value_string(value)

	@staticmethod
	def get_line_with_comments_removed(line_string):
		return line_string.split('#')[0] #cut off to right of comments

	@staticmethod
	def validate_incar_parameter_line(parameter_line_string):
		if parameter_line_string.count('=') != 1:
			raise Exception("Must have exactly one key value pair in one incar parameter line.")

	@staticmethod
	def get_processed_key_string(key_string):
		return (key_string.strip()).upper()

	@staticmethod
	def get_processed_value_string(value):
		return str(value).strip()

	@staticmethod
	def get_line_string(key, value):
		return Incar.get_processed_key_string(key) + Incar.output_separator_token + Incar.get_processed_value_string(value)