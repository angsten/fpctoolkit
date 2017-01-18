import os
import os
import os
from unittest2 import TestCase

from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.util.path import Path

class Test(TestCase):

	class_title = 'Incar'
	data_dir_path = Path.clean(os.path.dirname(__file__), 'data_'+class_title)

	def setUp(self):
		self.data_path = Path.clean(self.__class__.data_dir_path)

	def test_init(self):
		file_path = Path.clean(self.data_path, "incar_1")