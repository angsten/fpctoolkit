#from fpctoolkit.structure.structure import Structure

import numpy as np
import copy
import random
from phonopy import Phonopy
from phonopy.interface.vasp import read_vasp
import math

from fpctoolkit.io.file import File
from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.structure.site import Site
from fpctoolkit.structure.lattice import Lattice
from fpctoolkit.structure.site_collection import SiteCollection
from fpctoolkit.util.math.vector import Vector
from fpctoolkit.util.random_selector import RandomSelector
from fpctoolkit.util.path import Path



class Structure(object):
	"""
	Class for representing periodic crystal structures (lattice + basis).

	Holds Lattice instance (2D array) for the lattice and a SiteCollection instance for basis sites.

	For outputting to or inputting from file representations, this class is only compatible with the poscar file type (for now).
	"""

	def __init__(self, file_path=None, lattice=None, sites=None):
		"""
		file_path must be either a valid (relative or absolute) path to a poscar file or None
		lattice must be either a 2D array of floats or ints, a Lattice class instance, or None if file_path is specified
		sites must be either a list of sites, a SiteColleciton instance, or None if file_path is specified
		"""

		Structure.validate_constructor_arguments(file_path, lattice, sites)

		if file_path:
			self.from_poscar_file_path(file_path)
		else:
			self.lattice = Lattice(lattice)
			self.sites = SiteCollection(sites)


	@staticmethod
	def validate_constructor_arguments(file_path, lattice, sites):

		Path.validate(path=file_path, allow_none=True)

		if file_path == None:
			if lattice == None:
				raise Exception("A lattice must be specified.")
			else:
				Lattice.validate_lattice_representation(lattice)

			if not sites:
				raise Exception("A sites list or SiteColleciton instance must be specified.")
			else:
				SiteCollection.validate_sites(sites)

	@staticmethod
	def validate(structure):
		"""
		Verifies that structure is of type Structure and has a valid lattice and set of sites.
		"""

		if not isinstance(structure, Structure):
			raise Exception("structure is not of type Structure. Type is", type(structure))

		Lattice.validate_lattice_representation(structure.lattice)
		SiteCollection.validate_sites(structure.sites)


	def __str__(self):
		return str(self.lattice) + "\n".join(str(site) for site in self.sites) + "\n"


	def from_poscar_file_path(self, file_path):

		Path.validate(path=file_path, allow_none=False)
		Path.expand(file_path)

		poscar = Poscar(file_path)
		self.lattice = Lattice(poscar.lattice)
		self.sites = SiteCollection()

		poscar_coordinate_mode = poscar.coordinate_mode
		poscar_coordinates_list = poscar.coordinates

		species_index = 0
		for i, specie in enumerate(poscar.species_list):
			for j in range(poscar.species_count_list[i]):
				new_site = Site()
				new_site['coordinate_mode'] = poscar_coordinate_mode
				new_site['position'] = poscar_coordinates_list[species_index]
				new_site['type'] = specie

				self.sites.append(new_site)

				species_index += 1


	def to_poscar_file_path(self, file_path):
		lattice = self.lattice.to_array()
		species_list = self.sites.get_species_list()
		species_count_list = self.sites.get_species_count_list()
		coordinate_mode = self.sites.get_sorted_list()[0]['coordinate_mode']
		coordinates = self.sites.get_coordinates_list()

		SiteCollection.validate_sites_all_have_same_coordinate_mode(self.sites)

		poscar = Poscar(None, lattice, species_list, species_count_list, coordinate_mode, coordinates)
		poscar.write_to_path(file_path)


	def get_species_list(self):
		return self.sites.get_species_list()

	def get_species_count_list(self):
		return self.sites.get_species_count_list()

	def get_coordinates_list(self):
		return self.sites.get_coordinates_list()

	def get_formula_string(self):
		out_string = ''

		for i, species in enumerate(self.get_species_list()):
			species_count = self.get_species_count_list()[i]

			if species_count == 1:
				species_count_string = ''
			else:
				species_count_string = str(species_count)

			out_string += species + species_count_string

		return out_string



	@property
	def site_count(self):
		return len(self.sites)

	def convert_sites_to_coordinate_mode(self, coordinate_mode):
		if coordinate_mode == 'Direct':
			self.convert_sites_to_direct_coordinates()
		elif coordinate_mode == 'Cartesian':
			self.convert_sites_to_cartesian_coordinates()
		else:
			raise Exception("Given coordinate mode is not valid:", coordinate_mode)

	def convert_sites_to_cartesian_coordinates(self):
		"""
		Takes any site in sites that is in direct coordinates and changes
		its position and coordinate mode to be in cartesian coordinate system
		"""

		for site in self.sites:
			site.convert_to_cartesian_coordinates(self.lattice)

	def convert_sites_to_direct_coordinates(self):
		"""
		Takes any site in sites that is in cartesian coordinates and changes
		its position and coordinate mode to be in direct coordinate system
		"""

		for site in self.sites:
			site.convert_to_direct_coordinates(self.lattice)


	def randomly_displace_sites(self, max_displacement_magnitude, keep_first_site_at_origin=False):
		"""
		max_displacement_magnitude is the maximum displacement in a single cartesian direction (in angstroms)
		"""

		original_coordinate_mode = self.sites.get_coordinate_mode()

		self.convert_sites_to_cartesian_coordinates()

		for site in self.sites:
			for i in range(3):
				site['position'][i] += random.uniform(-1.0*max_displacement_magnitude, max_displacement_magnitude)

		if keep_first_site_at_origin:
			for site in self.sites:
				for i in range(3):
					site['position'][i] -= self.sites[0]['position'][i]


		self.convert_sites_to_coordinate_mode(original_coordinate_mode)

	def is_equivalent_to_structure(self, other_structure):
		"""
		Returns true if lattice vectors and atomic positions are all the same (within floating-point accuracy).
		"""

		if self.sites.get_coordinate_mode() != other_structure.sites.get_coordinate_mode():
			raise Exception("Coordinate modes are different - cannot compare the two structures.")

		for i, lattice_vector in self.lattice.to_array():
			for j in range(3):
				if abs(lattice_vector[j]-other_structure.lattice[i][j]) > 0.00001:
					return False

		for i, site in enumerate(self.sites):
			for j in range(3):
				if abs(site['position'][j]-other_structure.sites[i]['position'][j]) > 0.00001:
					return False

		return True

	def get_spacegroup_string(self, symprec=0.001):
		"""
		Returns string of spacegroup information like Imma (74).

		symprec controls the symmetry tolerance for atomic positions (in Angstroms)
		"""

		unit_cell_phonopy_structure = self.convert_structure_to_phonopy_atoms()
		supercell_dimensions_matrix = np.diag([1, 1, 1])

		phonon = Phonopy(unitcell=unit_cell_phonopy_structure, supercell_matrix=supercell_dimensions_matrix, symprec=symprec)

		symmetry = phonon.get_symmetry()

		return str(symmetry.get_international_table())

	def convert_structure_to_phonopy_atoms(self):
		"""
		Returns a PhonopyAtoms class (phonopy's representation of selfs)
		"""

		temporary_write_path = Path.get_temporary_path()

		Structure.validate(self)

		Path.validate_does_not_exist(temporary_write_path)
		Path.validate_writeable(temporary_write_path)

		self.to_poscar_file_path(temporary_write_path)
		phonopy_structure = read_vasp(temporary_write_path)

		Path.remove(temporary_write_path)

		return phonopy_structure


	def get_volume(self):
		"""
		Returns the volume of the structure's unit cell in Angstroms cubed.
		"""

		return self.lattice.get_volume()


	def get_magnitudes_and_angles(self):

		a = self.lattice[0]
		b = self.lattice[1]
		c = self.lattice[2]

		magnitudes = [np.linalg.norm(x) for x in [a, b, c]]


		alpha = (180.0/math.pi)*math.acos(np.dot(b,c)/(magnitudes[1]*magnitudes[2]))
		beta = (180.0/math.pi)*math.acos(np.dot(a,c)/(magnitudes[0]*magnitudes[2]))
		gamma = (180.0/math.pi)*math.acos(np.dot(a,b)/(magnitudes[0]*magnitudes[1]))

		return magnitudes + [alpha, beta, gamma]
