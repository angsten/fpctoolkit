from unittest2 import TestCase

from fpctoolki.io.file import File

class FileTest(TestCase):

	def setUp(self):
		pass

	def test_init(self):
		file = File()

		self.assertEqual(-1,2)