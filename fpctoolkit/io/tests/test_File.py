import os
from unittest2 import TestCase

from fpctoolkit.io.file import File
from fpctoolkit.util.path import Path

class Test(TestCase):

	class_title = 'File'
	data_dir_path = Path.clean(os.path.dirname(__file__), 'data_'+class_title)

	def setUp(self):
		self.data_path = Path.clean(self.__class__.data_dir_path)

	def test_init(self):
		with self.assertRaises(IOError):
			file = File(Path.clean(self.data_path, 'file.txt'))

		file = File()
		self.assertEqual(file.lines, [])
		self.assertEqual(file.load_path, None)

		file_path = Path.clean(self.data_path, 'file1.txt')
		file = File(file_path)
		self.assertEqual(file.lines[0], "This is a test file\r\n")
		self.assertEqual(file.lines[4], "line 5\r\n") 
		self.assertEqual(file.lines[6], "end of testing file")
		with self.assertRaises(IndexError):
			file.lines[7]

		self.assertEqual(file.load_path, file_path)

	def test_str(self):
		file = File(Path.clean(self.data_path, 'small_file.txt'))
		self.assertEqual(str(file), "Small file\r\nVery small\r\n")

		file = File(Path.clean(self.data_path, 'empty.txt'))
		self.assertEqual(str(file), "")		

	def test_add(self):
		pass
