import os
import os
import os
from unittest2 import TestCase

from fpctoolkit.structure.site import Site
from fpctoolkit.structure.lattice import Lattice
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.site_collection import SiteCollection
from fpctoolkit.util.path import Path

class Test(TestCase):

	class_title = 'Structure'
	data_dir_path = Path.clean(os.path.dirname(__file__), 'data_'+class_title)

	def setUp(self):
		self.data_path = Path.clean(self.__class__.data_dir_path)

	def test_init(self):
		site = Site()
		site['position'] = [0.1, 0.2, 0.4, "dir"]
		site['type'] = 'Ba'
		site_2 = Site()
		site_2['position'] = [0.6, 0.22, 0.44, "cart"]
		site_2['type'] = 'Ti'

		structure = Structure(lattice=Lattice(a=[3.4, 0.1, 0.2], b=[2.3, 5.0, 0.0], c=[0.0, 0.0, 1.0]), sites=SiteCollection([site, site_2]))

		self.assertEqual(structure.lattice.to_array(), [[3.4, 0.1, 0.2], [2.3, 5.0, 0.0], [0.0, 0.0, 1.0]])
		self.assertEqual(structure.sites.get_sorted_list()[0]['type'], 'Ba')
		self.assertEqual(structure.sites.get_coordinates_list(), [[0.1, 0.2, 0.4], [0.6, 0.22, 0.44]])


		file_path = Path.clean(self.data_path, "poscar_small")
		structure = Structure(file_path)

		self.assertEqual(structure.lattice.to_array(), [[5.0, 0.2, 0.1], [0.4, 6.0, 0.7], [-0.2, 0.0, 7.7]])
		self.assertEqual(structure.sites.get_sorted_list()[1]['coordinate_mode'], 'Direct')
		self.assertEqual(structure.get_coordinates_list(), [[0.11, 0.22, 0.33], [0.33, 0.22, 0.11], [0.22, 0.33, 0.11]])

		write_file_path = Path.clean(self.data_path, "poscar_small_rewritten")
		structure.to_poscar_file_path(write_file_path)

		structure = Structure(write_file_path)

		self.assertEqual(structure.lattice.to_array(), [[5.0, 0.2, 0.1], [0.4, 6.0, 0.7], [-0.2, 0.0, 7.7]])
		self.assertEqual(structure.sites.get_sorted_list()[1]['coordinate_mode'], 'Direct')
		self.assertEqual(structure.get_coordinates_list(), [[0.11, 0.22, 0.33], [0.33, 0.22, 0.11], [0.22, 0.33, 0.11]])


	def test_conversion(self):
		file_path = Path.clean(self.data_path, "big_posc")

		structure = Structure(file_path)
		structure_2 = Structure(file_path)

		structure_2.convert_sites_to_cartesian_coordinates()
		structure_2.convert_sites_to_direct_coordinates()
		print structure

		for i in range(len(structure.sites)):
			for j in range(3):
				self.assertTrue(structure.sites[i]['position'][j] - structure_2.sites[i]['position'][j] < 0.00000000001)