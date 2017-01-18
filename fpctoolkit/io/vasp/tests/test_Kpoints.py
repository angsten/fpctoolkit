import os
import os
import os
from unittest2 import TestCase

from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.util.path import Path

class Test(TestCase):

	class_title = 'Kpoints'
	data_dir_path = Path.clean(os.path.dirname(__file__), 'data_'+class_title)

	def setUp(self):
		self.data_path = Path.clean(self.__class__.data_dir_path)

	def test_init(self):
		file_path = Path.clean(self.data_path, "kpt_1")

		kpoints = Kpoints(file_path)

		self.assertEqual(kpoints.scheme,'Gamma')

		kpoints.scheme = "monkhorst"

		self.assertEqual(kpoints.scheme,'Monkhorst')

		self.assertEqual(kpoints.subdivisions_list, [4, 2, 4])

		kpoints.subdivisions_list = [6, 6, 8]

		self.assertEqual(kpoints.subdivisions_list, [6, 6, 8])

		new_path = Path.clean(self.data_path, "new_kpt_1")
		kpoints.write_to_path(new_path)

		kpoints_2 = Kpoints(new_path)

		self.assertEqual(kpoints_2.subdivisions_list, [6, 6, 8])
		self.assertEqual(kpoints.scheme,'Monkhorst')

		with self.assertRaises(Exception):
			kpoints_2.scheme = "Lonkhorst"

		with self.assertRaises(Exception):
			kpoints_2.subdivisions_list = ['2','4','5','6']


		kpoints_3 = Kpoints(scheme_str="Gamma", subdivisions_list=[4,6,8])
		self.assertEqual(str(kpoints_3),'Kpoints File\n0\nGamma\n4 6 8\n0 0 0\n')