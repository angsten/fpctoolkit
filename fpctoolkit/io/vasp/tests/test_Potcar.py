import os
import os
import os
from unittest2 import TestCase

from fpctoolkit.io.vasp.potcar import Potcar
from fpctoolkit.util.path import Path

class Test(TestCase):

	class_title = 'Potcar'
	data_dir_path = Path.clean(os.path.dirname(__file__), 'data_'+class_title)

	def setUp(self):
		self.data_path = Path.clean(self.__class__.data_dir_path)

	def test_init(self):
		potcar = Potcar(elements_list=['Ba'])

		self.assertEqual(potcar.get_titles(), ['PAW Ba_sv 17Apr2000'])
		self.assertEqual(potcar.get_elements_list(), ['Ba'])

		potcar_2 = Potcar(elements_list=['O','Ti','Ba'])
		self.assertEqual(potcar_2.get_titles(), ['PAW O 22Mar2012', 'PAW Ti_sv 26Sep2005', 'PAW Ba_sv 17Apr2000'])
		self.assertEqual(potcar_2.get_elements_list(), ['O', 'Ti', 'Ba'])