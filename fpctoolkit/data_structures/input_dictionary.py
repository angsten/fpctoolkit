#from fpctoolkit.data_structures.input_dictionary import InputDictionary





class InputDictionary(dict):
	"""
	Just like a dictionary but with constraints.

	Certain keys can be required to exist.
	"""

	def __init__(self, dictionary_initializer=None, required_keys_list=None):

		if dictionary_initializer == None:
			dictionary_initializer = {}

		super(InputDictionary, self).__init__(dictionary_initializer)

		self.required_keys_list = required_keys_list


