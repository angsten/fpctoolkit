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

		with self.assertRaises(IOError):
			file.write_to_path()

		file_path = Path.clean(self.data_path, 'file1.txt')
		file = File(file_path)
		self.assertEqual(file.lines[0], "This is a test file")
		self.assertEqual(file.lines[4], "line 5") 
		self.assertEqual(file.lines[6], "end of testing file")
		with self.assertRaises(IndexError):
			file.lines[7]

		self.assertEqual(file.load_path, file_path)

		file_path = Path.clean(self.data_path, 'small_file.txt')
		file = File(file_path)
		self.assertEqual(file.lines,['Small file', '  Very small  ', ''])

		file_path = Path.clean(self.data_path, 'empty.txt')
		file = File(file_path)
		self.assertEqual(file.lines,[])

		file_path = Path.clean(self.data_path, 'almost_empty.txt')
		file = File(file_path) #this file contains: line 1: '\n' line 2: ''
		self.assertEqual(file.lines, [''])

	def test_str(self):
		file = File(Path.clean(self.data_path, 'small_file.txt'))
		self.assertEqual(str(file), "Small file\n  Very small  \n\n")

		file = File(Path.clean(self.data_path, 'empty.txt'))
		self.assertEqual(str(file), "")

		file = File(Path.clean(self.data_path, 'almost_empty.txt')) #this file contains: line 1: '\n' line 2: ''
		self.assertEqual(str(file), "\n")

	def test_add(self):
		file_path = Path.clean(self.data_path, 'small_file.txt')
		file = File(file_path)
		add_str = "string to add"
		right_full_str = file + add_str
		self.assertEqual(right_full_str,"Small file\n  Very small  \n\nstring to add")

		l_add_str = "  left string to add"
		left_full_str = l_add_str + file

		self.assertEqual(left_full_str,"  left string to addSmall file\n  Very small  \n\n")

		file_path_1 = Path.clean(self.data_path, 'small_file.txt')
		file_path_2 = Path.clean(self.data_path, 'small_file_2.txt')
		first_file = File(file_path_1)
		second_file = File(file_path_2)

		final_file = first_file + second_file

		self.assertEqual(final_file.lines,['Small file', '  Very small  ', '', '', 'Small file 2', '  Not as small  ', ''])

	def test_overrides(self):
		file = File()
		self.assertFalse(file)
		file[2] = '  inserted line   '
		self.assertEqual(file.lines, ['', '', '  inserted line   '])
		file[1] = 'add this line\n and this one where index 1 was'
		self.assertEqual(file.lines, ['', 'add this line', ' and this one where index 1 was', '  inserted line   '])
		file[1] = 'replaced add this line'
		self.assertEqual(file.lines, ['', 'replaced add this line', ' and this one where index 1 was', '  inserted line   '])
		self.assertEqual(file.lines[1:3], ['replaced add this line', ' and this one where index 1 was'])
		del file[1]
		del file[0:2]
		self.assertEqual(file.lines, ['  inserted line   '])

		file += "new line added"
		self.assertEqual(file.lines, ['  inserted line   ', 'new line added'])

		file.insert(0,'inserted at beginning')
		file.insert(2,'right before new line added line')

		self.assertEqual(file.lines, ['inserted at beginning', '  inserted line   ', 'right before new line added line', 'new line added'])

		self.assertTrue(file)

		self.assertEqual(len(file),4)

		l = ['inserted at beginning', '  inserted line   ', 'right before new line added line', 'new line added']

		for x,item in enumerate(file):
			self.assertEqual(item,l[x])

	def test_write_to_path(self):
		file_path = Path.clean(self.data_path, 'small_file.txt')
		file = File(file_path)

		file[0] += " for line 0"
		file[3] = "line 3"
		file += ""
		file += "here\nand here"
		file += ""

		self.assertEqual(file.lines, ['Small file for line 0', '  Very small  ', '', 'line 3', '', 'here', 'and here', ''])

		file.write_to_path(Path.clean(self.data_path, 'small_file_ammended.txt'))

		file_2 = File(Path.clean(self.data_path, 'small_file_ammended.txt'))

		file_2[2] = "no more"
		file_2.write_to_path()

		file_3 = File(Path.clean(self.data_path, 'small_file_ammended.txt'))

		self.assertEqual(file_3.lines, ['Small file for line 0', '  Very small  ', 'no more', 'line 3', '', 'here', 'and here', ''])