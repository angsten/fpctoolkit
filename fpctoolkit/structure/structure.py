import numpy as np
import copy

from fpctoolkit.io.file import File
from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.structure.site import Site
from fpctoolkit.structure.lattice import Lattice
from fpctoolkit.structure.site_collection import SiteCollection
from fpctoolkit.util.vector import Vector

class Structure(object):
	"""Abstract crystal structure class.

	Holds 2D array for lattice and a SiteCollection instance
	Compatible with poscar file class only for now.
	"""
	def __init__(self, file_path=None, lattice=None, sites=None):

		if file_path: #load from file (only poscar supported for now)
			self.from_poscar_file_path(file_path)
		else:
			self.lattice = Lattice(lattice)

			if isinstance(sites, SiteCollection):
				self.sites = sites
			else:
				raise Exception("sites must be of SiteColleciton type")

	def __str__(self):
		return str(self.lattice) + "\n".join(str(site) for site in self.sites) + "\n"


	def from_poscar_file_path(self, file_path):
		poscar = Poscar(file_path)
		self.lattice = Lattice(poscar.lattice)
		self.sites = SiteCollection()

		species_index = 0
		for i, specie in enumerate(poscar.species_list):
			for j in range(poscar.species_count_list[i]):
				new_site = Site()
				new_site['coordinate_mode'] = poscar.coordinate_mode
				new_site['position'] = poscar.coordinates[species_index]
				new_site['type'] = specie

				self.sites.append(new_site)

				species_index += 1


	def to_poscar_file_path(self, file_path):
		lattice = self.lattice.to_array()
		species_list = self.sites.get_species_list()
		species_count_list = self.sites.get_species_count_list()
		coordinate_mode = self.sites.get_sorted_list()[0]['coordinate_mode']
		coordinates = self.sites.get_coordinates_list()

		for site in self.sites:
			if site['coordinate_mode'] != coordinate_mode:
				raise Exception("Not all coordinate modes in structure are consistent. Cannot write to poscar file.")

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


	def randomly_displace_site_positions(self, stdev, mean=0.0):
		"""Randomly displace all sites in separate random directions with
		dipslacement magnitude governed by a normal distribution.
		!!Parameters are given in angstroms!!
		These will be converted to direct coordinates for sites represented
		in direct coordinates.
		"""

		for site in self.sites:
			displacement_vector = Vector.get_random_vector(mean, stdev) #vector is in angstroms

			if site['coordinate_mode'] == 'Direct':
				#convert disp vec to direct coordinates
				displacement_vector = Vector.get_in_direct_coordinates(displacement_vector, self.lattice)

			site.displace(displacement_vector)

	def convert_sites_to_cartesian_coordinates(self):
		"""Takes any site in sites that is in direct coordinates and changes
		its position and coordinate mode to be in cartesian coordinate system
		"""

		for site in self.sites:
			if site['coordinate_mode'] == 'Direct':
				site['coordinate_mode'] = 'Cartesian'
				site['position'] = Vector.get_in_cartesian_coordinates(site['position'], self.lattice).to_list()

	def convert_sites_to_direct_coordinates(self):
		"""Takes any site in sites that is in cartesian coordinates and changes
		its position and coordinate mode to be in direct coordinate system
		"""

		for site in self.sites:
			if site['coordinate_mode'] == 'Cartesian':
				site['coordinate_mode'] = 'Direct'
				site['position'] = Vector.get_in_direct_coordinates(site['position'], self.lattice).to_list()

	def get_supercell(self, supercell_dimensions_list):
		"""
		Returns new structure that is a supercell of this structure
		Argument supercell_dimensions_list looks like [1,3,4]
		"""

		if not len(supercell_dimensions_list) == 3:
			raise Exception("supercell_dimensions_list must be of length 3")

		new_lattice = self.lattice.get_super_lattice(supercell_dimensions_list)
		new_sites = copyself.convert_sites_to_direct_coordinates()

		orig_lattice = self.getLattice()
		orig_direct_coords = self.getDirectCoords()
		num_atoms_list = self.getNumberAtomsList() #gives [4,4,6] - number of each atom in cell
		atom_num_multiplier = supercell_dimensions[0]*supercell_dimensions[1]*supercell_dimensions[2]

        #rewrite how many atoms are in poscar line index 6
        self.data[6] = ''
        for num in num_atoms_list:
            self.data[6] += str(num*atom_num_multiplier) + ' '
        self.data[6] = self.data[6][:-1] + '\n'

        #expand size of lattice
        for i in range(0,3):
            for j in range(0,3):
                self.lattice[i][j] *= supercell_dimensions[i]

        #make new atoms
        new_direct_coordinates = []
        for old_coord in orig_direct_coords:
            for a in range(0,supercell_dimensions[0]):
                for b in range(0,supercell_dimensions[1]):
                    for c in range(0,supercell_dimensions[2]):
                        a_frac = float(a)/float(supercell_dimensions[0])
                        b_frac = float(b)/float(supercell_dimensions[1])
                        c_frac = float(c)/float(supercell_dimensions[2])

                        new_direct_coordinates.append([old_coord[0]/supercell_dimensions[0]+a_frac,old_coord[1]/supercell_dimensions[1]+b_frac,old_coord[2]/supercell_dimensions[2]+c_frac])

        self.directCoordinates = new_direct_coordinates
