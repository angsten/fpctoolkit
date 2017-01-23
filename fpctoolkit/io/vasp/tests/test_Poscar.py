import os
import os
import os
from unittest2 import TestCase

from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.util.path import Path

class Test(TestCase):

	class_title = 'Poscar'
	data_dir_path = Path.clean(os.path.dirname(__file__), 'data_'+class_title)

	def setUp(self):
		self.data_path = Path.clean(self.__class__.data_dir_path)

	def test_init(self):
		file_path = Path.clean(self.data_path, "poscar_small")
		poscar = Poscar(file_path)

		self.assertEqual(poscar.species_list, ['Si', 'O'])
		self.assertEqual(poscar.lines, ['Poscar', '1.0', '5.0 0.2 0.1', '0.4\t 6.0   0.7', '-0.2   0.0  7.7    ', 'Si   O', '2  1', 'Direct', '0.11 0.22 0.33', '0.33 0.22 0.11', '0.22 0.33 0.11  '])
		self.assertEqual(poscar.species_count_list, [2, 1])
		self.assertEqual(poscar.coordinate_system, 'Direct')
		self.assertEqual(poscar.coordinates, [[0.11, 0.22, 0.33], [0.33, 0.22, 0.11], [0.22, 0.33, 0.11]])


		lattice = [[2.2, 2.3, 2.1], [1.2, 3.3, 0.0], [-1.2, -2.2, 4.4]]
		species_list = ['K', 'V', 'O']
		species_count_list = [1, 2, 3]
		coordinate_system = 'cart'
		coordinates = [[0.2, 0.3, 0.4], [0.5, 0.5, 0.1], [-0.01, 0.1, 0.01], [2.33, 6.5, 3.2], [0.0, 0.1, -0.1], [0.1, 0.5, 0.5]]
		poscar = Poscar(None, lattice, species_list, species_count_list, coordinate_system, coordinates)

		self.assertEqual(poscar.species_list, ['K', 'V', 'O'])
		self.assertEqual(poscar.lines, ['Poscar', '1.0', '2.2 2.3 2.1', '1.2 3.3 0.0', '-1.2 -2.2 4.4', 'K V O', '1 2 3', 'Cartesian', '0.2 0.3 0.4', '0.5 0.5 0.1', '-0.01 0.1 0.01', '2.33 6.5 3.2', '0.0 0.1 -0.1', '0.1 0.5 0.5'])
		self.assertEqual(poscar.species_count_list, [1, 2, 3])
		self.assertEqual(poscar.coordinate_system, 'Cartesian')
		self.assertEqual(poscar.coordinates, coordinates)
		
	def test_loaded(self):
		pass