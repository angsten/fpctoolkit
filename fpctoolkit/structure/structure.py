#from fpctoolkit.structure.structure import Structure

import numpy as np
import copy

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


