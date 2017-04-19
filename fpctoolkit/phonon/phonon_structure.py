#from fpctoolkit.phonon.phonon_structure import PhononStructure

import numpy as np
import copy
from collections import OrderedDict
import math
import cmath

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.structure_manipulator import StructureManipulator
from fpctoolkit.phonon.normal_coordinate import NormalCoordinate


class PhononStructure(object):
	"""
	Represents a structure whose distortions are characterized by a set of 'complex normal coordinates', Q_q,j (see around page 298 of Born and Huang and pages preceding).
	"""

	def __init__(self, primitive_cell_structure, phonon_band_structure, supercell_dimensions_list, normal_coordinate_instances_list=None):
		"""
		primitive_cell_structure should be the primitive cell Structure class instance that was used to generate the phonon band structure.

		phonon_band_structure should be a PhononBandStructure instance with, at minimim, normal modes for the 'permitted wave vectors' (38.10, pg 295 Born and Huang)
		-->For example, if a 2x1x1 supercell is expected, the following q points must be provided: (-1/2, 0, 0), (0, 0, 0)

		supercell_dimensions

		if normal_coordinate_instances_list, this list is used to set the normal coordinates, else, the normal coordinates are initialized to zero.
		"""

		Structure.validate(primitive_cell_structure)

		self.primitive_cell_structure = primitive_cell_structure
		self.phonon_band_structure = phonon_band_structure
		self.supercell_dimensions_list = supercell_dimensions_list


		self.reference_supercell_structure = StructureManipulator.get_supercell(primitive_cell_structure, supercell_dimensions_list)



		self.validate_permitted_wave_vectors_exist()


		self.number_of_normal_coordinates = self.primitive_cell_structure.site_count*3*supercell_dimensions_list[0]*supercell_dimensions_list[1]*supercell_dimensions_list[2]


		if normal_coordinate_instances_list != None:
			if len(normal_coordinate_instances_list) != self.number_of_normal_coordinates:
				raise Exception("The number of given normal coordinates is not equal to the number needed to describe the structural distortions. Normal coordinates list given is", normal_coordinate_instances_list)
			else:
				self.normal_coordinates_list = copy.deepcopy(normal_coordinate_instances_list)
		else:
			self.initialize_normal_coordinates_list()

	def __str__(self):
		return "[\n" + "\n".join(str(normal_coordinate) for normal_coordinate in self.normal_coordinates_list) + "\n]"


	def initialize_normal_coordinates_list(self):

		self.normal_coordinates_list = []

		for normal_mode in self.phonon_band_structure.get_list_of_normal_modes():
			self.normal_coordinates_list.append(NormalCoordinate(normal_mode_instance=normal_mode, complex_coefficient=0.0+0.0j))


	def validate_permitted_wave_vectors_exist(self):
		"""
		Validates that (at minimum) all permitted wavevectors for the given supercell_dimensions are in phonon_band_structure.
		"""

		permitted_q_vectors_list = self.get_permitted_wave_vectors_listt()

		for q_vector in permitted_q_vectors_list:
			if q_vector not in self.phonon_band_structure:
				raise Exception("Phonon band structure does not contain all permitted q_vectors. Missing ", q_vector)





	def get_permitted_wave_vectors_listt(self):
		"""
		Using equation 38.10 from B+H, determine all permitted wave vectors for the given supercell dimensions (resulting q's are in
		fractional coordinates)
		"""

		return PhononStructure.get_permitted_wave_vectors_list(self.supercell_dimensions_list)



	def get_distorted_structure(self):
		"""
		Returns a supercell of self.primitive_cell_structure with dimensions self.supercell_dimensions_list with the phonon eigen_displacements applied, as
		controlled by self.normal_coordinates_list
		"""

		distorted_structure = copy.deepcopy(self.reference_supercell_structure)

		for site_count, site in enumerate(distorted_structure.sites):

			#index to cite number in the primitive cell - can range from 1 to Nat, where there are Nat in the primitive cell
			atom_index = 1 + int(site_count/(self.supercell_dimensions_list[0]*self.supercell_dimensions_list[1]*self.supercell_dimensions_list[2]))

			#this marks the cell the site is in - for instance, 1, 1, 1 in a 2x2x2 supercell means I'm in the center of the supercell
			site_supercell_position = [site['position'][i]*self.supercell_dimensions_list[i] for i in range(3)] 

			cartesian_displacement = [0.0, 0.0, 0.0]

			for normal_coordinate in self.normal_coordinates_list:
				q_vector = normal_coordinate.normal_mode.q_point_fractional_coordinates
				eigen_displacements_vector = normal_coordinate.normal_mode.eigen_displacements_list[0*atom_index:3*atom_index]

				cartesian_displacement += normal_coordinate.complex_coefficient*eigen_displacements_vector*cmath.exp(2.0*math.pi*(1.0j)*np.dot(q_vector, site_supercell_position))

		pass


	def set_translational_coordinates_to_zero(self):
		"""
		Sets all components of self.Q_coordinates_list that correspond to a translational normal mode that doesn't affect the structure's energy.
		"""

		pass

	@staticmethod
	def get_normal_coordinates_list_from_supercell_structure(self, supercell_structure):
		"""
		Returns a list of complex normal coordinates (Q) based on the current phonon band structure and the displacements in supercell_structure.
		Supercell_structure must be consistent in dimensions with self.supercell_dimensions.
		"""

		pass


	@staticmethod
	def get_permitted_wave_vectors_list(supercell_dimensions_list):
		"""
		Using equation 38.10 from B+H, determine all permitted wave vectors for the given supercell dimensions (resulting q's are in
		fractional coordinates)

		For example, for a 2x1x1 supercell, returned q points will be [(-0.5, 0, 0), (0, 0, 0)]
		"""

		permitted_q_vectors_list = []
		L_x = supercell_dimensions_list[0]
		L_y = supercell_dimensions_list[1]
		L_z = supercell_dimensions_list[2]

		for l_x in range(-L_x, L_x):
			for l_y in range(-L_y, L_y):
				for l_z in range(-L_z, L_z):
					q_point_x = float(l_x)/float(L_x)
					q_point_y = float(l_y)/float(L_y)
					q_point_z = float(l_z)/float(L_z)

					q_point = (q_point_x, q_point_y, q_point_z)

					q_point_permitted = True

					for q_component in q_point:
						if (q_component < (-0.5)) or (q_component >= (0.5)):
							q_point_permitted = False

					if q_point_permitted:
						permitted_q_vectors_list.append(q_point)

		if len(permitted_q_vectors_list) != L_x*L_y*L_z:
			raise Exception("Number of permitted wave-vectors must equal the number of cells in the supercell.")

		return permitted_q_vectors_list