import os
import json

from fpctoolkit.io.file import File
from fpctoolkit.util.path import Path
import fpctoolkit.util.file_util as fu

class Potcar(File):
	"""
	Can initialize from an existing potcar file (Potcar('./POTCAR'))
	Can initialize from a string of elements and whether or not to use LDA or GGA (Potcar(['Ba','Ti','O'],lda=False))
		In this case, set of predefined potcars will be used
		Assumes lda = True
	Can initialize from a list of basenames which might look like ['Ba_sv', 'Ti_sv', 'O']
	Can initialize from a minimal_form which looks like {'basenames':['Ba_sv', 'Ti_sv', 'O'], 'calculation_type':'lda'}
	"""

	element_mapping_path = Path.clean(os.path.dirname(__file__),'potcar_element_mapping.json')

	def __init__(self, file_path=None, elements_list=None, basenames_list=None, calculation_type='lda', minimal_form=None):

		super(Potcar, self).__init__(file_path)

		if file_path:
			if self.get_lines_containing_string("PAW_PBE"): #be careful if potcars different than used to in future
				self.calculation_type = 'gga'
			else:
				self.calculation_type = 'lda'

		if minimal_form:
			calculation_type = minimal_form['calculation_type']
			basenames_list = minimal_form['basenames']

		if elements_list or basenames_list:
			self.calculation_type = calculation_type

			element_mapping_file = File(Potcar.element_mapping_path)
			element_mapping_string = str(element_mapping_file)
			potcar_dict = json.loads(element_mapping_string)

			base_path = potcar_dict[calculation_type]['path']

			if elements_list:
				potcar_paths = [Path.clean(base_path, potcar_dict[calculation_type][element], 'POTCAR') for element in elements_list]
			elif basenames_list:
				potcar_paths = [Path.clean(base_path, basename, 'POTCAR') for basename in basenames_list]

			concatenated_file = File()
			for path in potcar_paths:
				concatenated_file = concatenated_file + File(path)

			self.lines = concatenated_file.lines

	def get_titles(self):
		"""Returns list like ['PAW Ba_sv 17Apr2000', 'PAW Ti_sv 26Sep2005', 'PAW O 22Mar2012']"""

		titles_list = self.get_lines_containing_string('TITEL')
		
		return [x.split("= ")[1].rstrip() for x in titles_list]

	def get_elements_list(self):
		"""Returns list like ['Ba', 'Ti', 'O']"""

		return [x.split(" ")[1].split("_")[0] for x in self.get_titles()]

	def get_basenames_list(self):
		"""Returns list like ['Ba_sv', 'Ti_sv', 'O']"""

		return [x.split(" ")[1] for x in self.get_titles()]

	def get_minimal_form(self):
		"""Returns minimal form (a dict like {'basenames':['Ba_sv', 'Ti_sv', 'O'], 'calculation_type':'lda'])"""

		return {'basenames':self.get_basenames_list(), 'calculation_type':self.calculation_type}