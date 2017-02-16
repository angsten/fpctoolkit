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

	def randomly_displace_site_positions(self, stdev, enforced_minimum_atomic_distance=None, max_displacement_distance=None, mean=0.0, types_list=None):
		"""
		Randomly displace all sites in separate random directions with
		displacement magnitude governed by a normal distribution.
		Note: mean effectively is the shell about which atoms on average sit around there original position.
		!!Parameters are given in angstroms!!
		These will be converted to direct coordinates for sites represented
		in direct coordinates. Modifies self.

		If types_list is specified, only sites with type in types_list will be perturbed

		returns False if unable to satisfy any constraints (and reverts structure to its original), true else
		"""

		if types_list == None:
			types_list = []

		sites_copy = copy.deepcopy(self.sites)

		for site in self.sites:

			if site['type'] not in types_list:
				continue

			if enforced_minimum_atomic_distance:
				success = self.randomly_displace_site_position_with_minimum_distance_constraints(site, stdev, enforced_minimum_atomic_distance, max_displacement_distance, mean)

				if not success:
					self.sites = sites_copy #restore structure to original form
					return False
			else:
				self.randomly_displace_site_position(site, stdev, max_displacement_distance, mean)

		return True

	def randomly_displace_site_position_with_minimum_distance_constraints(self, site, stdev, enforced_minimum_atomic_distance, max_displacement_distance=None, mean=0.0, max_attempt_count=400):
		"""
		Calls randomly_displace_site_position for a site. Tries until no atoms are within enforced_minimum_atomic_distance (angstroms) of the atom being perturbed.
		Maxes out after a finite number of tries (returns false)
		"""

		original_position = copy.deepcopy(site['position'])

		for attempt_count in range(max_attempt_count):
			self.randomly_displace_site_position(site, stdev, max_displacement_distance, mean)

			if self.any_sites_are_too_close(site, enforced_minimum_atomic_distance):
				site['position'] = copy.deepcopy(original_position)
				continue
			else:
				return True

		return False

	def randomly_displace_site_position(self, site, stdev, max_displacement_distance=None, mean=0.0):
		"""
		Randomly displaces a single site in separate random directions with
		displacement magnitude governed by a normal distribution.
		!!Parameters are given in angstroms!!
		Site will be converted to direct coordinates for sites represented
		in direct coordinates. Modifies site.
		"""

		if max_displacement_distance and max_displacement_distance < 0.0:
			raise Exception("Max displacement distance must be a non-negative quantity")

		displacement_vector = Vector.get_random_vector(mean, stdev) #vector is in angstroms

		if max_displacement_distance and (displacement_vector.magnitude > max_displacement_distance):
			corrector_fraction = max_displacement_distance/displacement_vector.magnitude
			displacement_vector = displacement_vector * corrector_fraction

		if site['coordinate_mode'] == 'Direct':
			#convert disp vec to direct coordinates
			displacement_vector = Vector.get_in_direct_coordinates(displacement_vector, self.lattice)

		site.displace(displacement_vector)


	def any_sites_are_too_close(self, test_site, enforced_minimum_atomic_distance, N_max=3):
		"""
		Returns True if any site in this structure is within enforced_minimum_atomic_distance (angstroms) of test_site
		Ignores if test_site is the same object (address compared) as a site in the structure. 
		N_max controls how many images to search. Higher means higher accuracy in weird sheared structures
		"""

		self.convert_sites_to_direct_coordinates()

		test_site_fractional_coordinates = test_site['position'] if test_site['coordinate_mode'] == 'Direct' else Vector.get_in_direct_coordinates(test_site['position'])

		for site in self.sites:
			if test_site is site: #don't consider case where these are the same site objects
				continue

			minimum_distance = Vector.get_minimum_distance_between_two_periodic_points(test_site_fractional_coordinates, site['position'], self.lattice, N_max)

			if minimum_distance < enforced_minimum_atomic_distance:
				return True

		return False


	def convert_sites_to_cartesian_coordinates(self):
		"""Takes any site in sites that is in direct coordinates and changes
		its position and coordinate mode to be in cartesian coordinate system
		"""

		for site in self.sites:
			site.convert_to_cartesian_coordinates(self.lattice)

	def convert_sites_to_direct_coordinates(self):
		"""Takes any site in sites that is in cartesian coordinates and changes
		its position and coordinate mode to be in direct coordinate system
		"""

		for site in self.sites:
			site.convert_to_direct_coordinates(self.lattice)

	def get_supercell(self, supercell_dimensions_list):
		"""
		Returns new structure that is a supercell of this structure (self)
		Argument supercell_dimensions_list looks like [1,3,4]
		"""

		if not len(supercell_dimensions_list) == 3:
			raise Exception("Argument supercell_dimensions_list must be of length 3")

		for dimension in supercell_dimensions_list:
			if not int(dimension) == dimension:
				raise Exception("Only integer values accepted for supercell dimension factors.")

		self.convert_sites_to_direct_coordinates()

		new_lattice = self.lattice.get_super_lattice(supercell_dimensions_list)
		new_sites = SiteCollection()

		for original_site in self.sites:
			for a in range(supercell_dimensions_list[0]):
				for b in range(supercell_dimensions_list[1]):
					for c in range(supercell_dimensions_list[2]):
						a_frac = float(a)/float(supercell_dimensions_list[0])
						b_frac = float(b)/float(supercell_dimensions_list[1])
						c_frac = float(c)/float(supercell_dimensions_list[2])

						new_site = copy.deepcopy(original_site)
						old_position = original_site['position']
						new_site['position'] = [old_position[0]/supercell_dimensions_list[0]+a_frac, old_position[1]/supercell_dimensions_list[1]+b_frac, old_position[2]/supercell_dimensions_list[2]+c_frac]
						new_sites.append(new_site)


		return Structure(lattice=new_lattice, sites=new_sites)
