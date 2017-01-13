import os
import json

from fpctoolkit.io.file import File
from fpctoolkit.util.path import Path

class Potcar(File):
	"""
	Can initialize from an existing potcar file (Potcar('./POTCAR'))
	Can initialize from a string of elements and whether or not to use LDA or GGA (Potcar(['Ba','Ti','O'],lda=False))
		In this case, set of predefined potcars will be used
		Assumes lda = True
	"""

	element_mapping_path = Path.clean(os.path.dirname(__file__),'potcar_element_mapping.json')

	def __init__(self, file_path=None, elements_list=None, calculation_type='lda'):
		super(Potcar,self).__init__(file_path)

		if elements_list:
			json_string = str(File(Potcar.element_mapping_path))
			potcar_data = json.loads(json_string)

			base_path = potcar_data[calculation_type]['path']

			potcar_paths = [Path.clean(base_path, potcar_data[calculation_type][element], 'POTCAR') for element in elements_list]

			print potcar_paths

			for path in potcar_paths:
				self.data += File(path).data

			print self



