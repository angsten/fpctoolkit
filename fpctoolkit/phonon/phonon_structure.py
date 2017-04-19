#from fpctoolkit.phonon.phonon_structure import PhononStructure

import numpy as np
from collections import OrderedDict

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.structure_manipulator import StructureManipulator


class PhononStructure(object):
	"""
	Represents a structure whose distortions are characterized by a set of 'complex normal coordinates', Q_q,j (see around page 298 of Born and Huang and pages preceding).
	"""

	def __init__(self, primitive_cell_structure, phonon_band_structure, supercell_dimensions_list):
		"""
		primitive_cell_structure should be the primitive cell Structure class instance that was used to generate the phonon band structure.

		phonon_band_structure should be a PhononBandStructure instance with, at minimim, normal modes for the 'permitted wave vectors' (38.10, pg 295 Born and Huang)
		-->For example, if a 2x1x1 supercell is expected, the following q points must be provided: (-1/2, 0, 0), (0, 0, 0)

		supercell_dimensions

		"""

		Structure.validate(primitive_cell_structure)

		self.primitive_cell_structure = primitive_cell_structure
		self.phonon_band_structure = phonon_band_structure
		self.supercell_dimensions_list = supercell_dimensions_list


		self.reference_supercell_structure = StructureManipulator.get_supercell(primitive_cell_structure, supercell_dimensions_list)



		self.validate_permitted_wave_vectors_exist()




		self.Q_coordinates_list = [0+0j]*self.reference_supercell_structure.site_count*3


	def validate_permitted_wave_vectors_exist(self):
		"""
		Validates that (at minimum) all permitted wavevectors for the given supercell_dimensions are in phonon_band_structure.
		"""

		pass





	def get_permitted_wave_vectors_list(self):
		"""
		Using equation 38.10 from B+H, determine all permitted wave vectors for the given supercell dimensions (resulting q's are in
		fractional coordinates)
		"""

		permitted_q_vectors_list = []
		L_x = self.supercell_dimensions_list[0]
		L_y = self.supercell_dimensions_list[1]
		L_z = self.supercell_dimensions_list[2]

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



	def get_distorted_structure(self):
		"""
		Returns a supercell self.primitive_cell_structure with dimensions self.supercell_dimensions_list with the phonon eigen_displacements applied, as
		controlled by self.Q_coordinates_list
		"""

		pass

	@staticmethod
	def get_normal_coordinates_list_from_supercell_structure(self, supercell_structure):
		"""
		Returns a list of complex normal coordinates (Q) based on the current phonon band structure and the displacements in supercell_structure.
		Supercell_structure must be consistent in dimensions with self.supercell_dimensions.
		"""

		pass

	def set_translational_coordinates_to_zero(self):
		"""
		Sets all components of self.Q_coordinates_list that correspond to a translational normal mode that doesn't affect the structure's energy.
		"""

		pass

