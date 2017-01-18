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
	"""

	element_mapping_path = Path.clean(os.path.dirname(__file__),'potcar_element_mapping.json')

	def __init__(self, file_path=None, elements_list=None, calculation_type='lda'):

		super(Potcar, self).__init__(file_path)

		if elements_list:
			element_mapping_file = File(Potcar.element_mapping_path)
			element_mapping_string = str(element_mapping_file)
			potcar_dict = json.loads(element_mapping_string)

			base_path = potcar_dict[calculation_type]['path']
			potcar_paths = [Path.clean(base_path, potcar_dict[calculation_type][element], 'POTCAR') for element in elements_list]

			concatenated_file = File()
			for path in potcar_paths:
				concatenated_file = concatenated_file + File(path)

			self.lines = concatenated_file.lines

	def get_titles(self):
		titles_list = self.get_lines_containing_string('TITEL')
		
		return [x.split("= ")[1].rstrip() for x in titles_list]

	def get_elements_list(self):
		return [x.split(" ")[1].split("_")[0] for x in self.get_titles()]