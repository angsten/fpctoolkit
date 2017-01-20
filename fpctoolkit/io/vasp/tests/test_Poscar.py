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

		self_assertEqual(str(poscar), "Poscar\n1.0\n5.91255829126 0.2 0.11\n0.11	 5.45136487181   0.44 \n 	 -0.23   0.0  7.7458873974   \n Si   O\n2  1\nDirect\n0.654800064878 0.935430180228 0.840085320553\n0.554176871053 0.502176431073 0.862746120421\n0.57417497541 0.457931672533 0.426117368848\n\n\n")
		self_assertEqual(poscar.lattice, [[5.91255829126, 0.2, 0.11], [0.11, 5.45136487181, 0.44], [-0.23, 0.0, 7.7458873974]])
		self_assertEqual(poscar.species_list, ['Si', 'O'])
		self_assertEqual(poscar.species_count_list, [2,1])
		self_assertEqual(poscar.coordinate_system, 'Direct')
		self_assertEqual(poscar.coordinates, [[0.654800064878, 0.935430180228, 0.840085320553], [0.554176871053, 0.502176431073, 0.862746120421], [0.57417497541, 0.457931672533, 0.426117368848]])

		#with self.assertRaises(Exception):
		#	incar['proper ty'] = 'value'

		#with self.assertRaises(Exception):
		#	incar += 'PREC = repeat'
		
	def test_loaded(self):
		pass