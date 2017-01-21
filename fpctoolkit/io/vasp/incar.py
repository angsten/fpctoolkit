from collections import OrderedDict

from fpctoolkit.io.file import File
import fpctoolkit.util.string_util as su

class Incar(File):
	"""Multiple parameters assigned in one line not supported
		
	Lines with no equals sign are treated as comments
	Anything after a # is treated as a comment
	= signs after # will be replaced with 'equals' to avoid errors
	Redundant whitespace is removed automatically, keys in file are
	auto-capitalized.
	Cannot have multiple non-comment = signs in file
	Example functionalities:
		incar = Incar()
		incar[0] = 'comment line here'
		incar['isif'] = 3
		incar['EDIFF'] = 0.0000001
		incar['prec'] = 'Accurate'
		ediff in incar  #returns true (it has the key)
		del incar['ediff']
		incar += 'ediff = 0.001' #errors - already have ediff
		incar [7] = 'another comment'

	"""

	output_separator_token = " = "

	def __init__(self, file_path=None):
		super(Incar, self).__init__(file_path)

		#remove only-whitespace-containing lines at end
		self.trim_trailing_whitespace_only_lines()

		#for each line in incar:
		#make sure keys are capitalized, no redundant white-space in non-comment parts
		#make sure no more than one assigment on each line
		self.modify_lines(Incar.standardize_line)

		#update dict here from loaded file text lines
		self.update_dictionary_from_file_lines()

	def __str__(self):
		self.modify_lines(Incar.standardize_line)

		return super(Incar, self).__str__()

	def __setitem__(self, key, value):
		if isinstance(key, int): #treat as file line index setter: incar[2] = 'file line string'
			value = Incar.standardize_line(str(value)) #value is a file line - standardize
			super(Incar, self).__setitem__(key, value)
			self.update_dictionary_from_file_lines()
		elif isinstance(key, basestring): #key must be a dictionary key of type string
			key = Incar.get_processed_key_string(key)
			line_string = Incar.get_line_string(key, value) #'ISIF = 2'

			if key not in self.dict:
				super(Incar, self).__iadd__(line_string) #File += line_string call
			else: #find actual line with this key and update the value
				line_index = self.get_line_index_of_key(key)
				self.lines[line_index] = line_string
			
			self.dict[key] = Incar.get_processed_value_string(value)
		else:
			raise Exception("Key must be either of int or string type")

	def __iadd__(self, line_string):
		super_value = super(Incar, self).__iadd__(Incar.standardize_line(str(line_string)))
		self.update_dictionary_from_file_lines()
		return super_value


	def __getitem__(self, key):
		if not isinstance(key, basestring): #treat as file line index getter
			return super(Incar, self).__getitem__(key)
		else:
			key = Incar.get_processed_key_string(key)
			if key in self.dict:
				return self.dict[key]

	def __delitem__(self, key):
		if not isinstance(key, basestring):
			super(Incar, self).__delitem__(key)
		else:
			key = Incar.get_processed_key_string(key)

			if key in self.dict:
				del self.lines[self.get_line_index_of_key(key)]
				del self.dict[key]

	def __contains__(self, key):
		if not isinstance(key, basestring):
			return super(Incar, self).__contains__(key)
		else:
			key = Incar.get_processed_key_string(key)
			return (key in self.dict)


	def update_dictionary_from_file_lines(self):
		self.dict = OrderedDict()

		for (key, value) in self.get_key_value_pairs_from_file_lines():
			if key in self:
				raise Exception("Incar file contains key " + key + " twice.")
			else:
				self.dict[key] = value

	def get_key_value_pairs_from_file_lines(self):
		"""Get key value pairs for lines with valid separator char in it ('=').
			This method will not find multiple key value pairs in one line.
		"""
		kv_function = Incar.get_key_value_pair_from_file_line

		return [kv_function(line) for line in self.lines if kv_function(line)]

	def get_line_index_of_key(self, key):
		"""Returns the index of the line containing key as a valid parameter assignment"""
		indices = []
		for i, line in enumerate(self.lines):
			if (line.upper()).find(key + ' =') != -1:
				indices.append(i)

		if len(indices) > 1:
			raise Exception("Incar file contains " + key + " key twice.")
		elif len(indices) == 0:
			return None
		else:
			return indices[0]
		# line_index_list = self.get_indices_of_lines_containing_key(key)
		# filtered_line_index_list = filter(lambda x: self[x].find('=') != -1, line_index_list) #only accept those with an assignment

		# if len(filtered_line_index_list) > 1:
		# 	raise Exception("Incar file contains " + key + " key twice.")

		# return filtered_line_index_list[0]

	def get_indices_of_lines_containing_key(self, key):
		"""Applies modifier to each line before searching"""
		indices = []	
		new_lines = [Incar.get_line_with_comments_removed(line) for line in self.lines]

		for i, line in enumerate(new_lines):
			if (line.upper()).find(key) != -1:
				indices.append(i)

		return indices


	@staticmethod
	def get_key_value_pair_from_file_line(line_string):
		"""Takes '  Isif = 2 # comment ' and gives (ISIF, 2)
			If line has no assignment, returns None

		"""
		line_string = line_string.split('#')[0]
		line_string = line_string.strip()
		line_string = su.remove_extra_spaces(line_string)

		equals_split = line_string.split('=')

		if len(equals_split) != 2:
			return None

		key = Incar.get_processed_key_string(equals_split[0])
		value = Incar.get_processed_value_string(equals_split[1])

		return (key, value)


	@property
	def parameter_line_strings_list(self):
		#gives all lines with comments stripped which contain '=' character
		modifier = lambda x: x.split('#')[0]
		param_list = [Incar.get_line_with_comments_removed(line) for line in self.get_lines_containing_string("=", modifier)]
		return param_list



	@staticmethod
	def get_line_with_comments_removed(line_string):
		return line_string.split('#')[0] #cut off to right of comments

	@staticmethod
	def validate_incar_parameter_line(parameter_line_string):
		non_comment_parameter_line_string = parameter_line_string.split('#')[0]
		if non_comment_parameter_line_string.count('=') != 1:
			raise Exception("Must have exactly one key value pair in one incar parameter line.")


	@staticmethod
	def get_processed_key_string(key_string):
		modified_key_string = (key_string.strip()).upper()

		if ' ' in modified_key_string:
			raise Exception("Incar keys should not contain an internal space")
		else:
			return modified_key_string

	@staticmethod
	def get_processed_value_string(value):
		return str(value).strip()


	@staticmethod
	def get_line_string(key, value):
		line_string = Incar.get_processed_key_string(key) + Incar.output_separator_token + Incar.get_processed_value_string(value)
		return line_string

	@staticmethod
	def standardize_line(line_string):
		"""Cases are:
			''
			'   '
			'All comment, no hashtag'
			'Comment no hashtag #then hashtag'
			'#all comment with hashtag'
			'#comment with = sign'
			'isif = 2'
			'isif  = 2' or 'isif=2' ...
			'isif = 2 #with comment'
			'isif = 2 #with comment with = sign'
			'isif = 2 algo = fast' is not valid
		"""
		ist = Incar.output_separator_token

		line_string = line_string.strip()
		if not line_string: 
			return line_string #handles '' and '   ' cases

		non_comment_part = line_string.split('#')[0]
		comment_part = "" if line_string.find('#') == -1 else "#" + line_string.split('#')[1].replace('=','equals')

		if line_string[0] == '#': #whole line is comment case
			return comment_part

		line_string = non_comment_part + comment_part
		if non_comment_part.find("=") == -1: #all comment cases
			return line_string

		if non_comment_part.count('=') != 1:
			raise Exception("incar lines must contain exactly one assignment")

		#first token must be key now, second token must be value
		key = Incar.get_processed_key_string(non_comment_part.split('=')[0])
		value = Incar.get_processed_value_string(non_comment_part.split('=')[1])

		if not key or not value:
			raise Exception("Incar has incorrect assignment: Either no key or no value found")

		if comment_part:
			comment_part = " " + comment_part

		return key + ist + value + comment_part