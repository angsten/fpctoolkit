#from fpctoolkit.structure.perovskite import Perovskite

from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.site import Site
from fpctoolkit.structure.lattice import Lattice
from fpctoolkit.structure.site_collection import SiteCollection

class Perovskite(Structure):
	"""Abstract crystal structure class for perovskite-derived structures

	Contains many helper functions for generating distorted/perfect
	perovskite structures.

	The constructor creates a perfect cubic perovskite based on:
		supercell dimensions (e.g., [4, 4, 2])
		lattice (e.g., [[4.0, 0.0, 0.0], [...], [...]] or Lattice class)
		species_list (e.g., ['Ba', 'Ti', 'O'])

	Can also load in a perovskite structure from a poscar file at file_path
	"""
	
	#offset convention for A, B, OI, OII, OIII in direct coords
	position_offsets = [[0.0,0.0,0.0], [0.5,0.5,0.5], [0.5,0.0,0.5], [0.5,0.5,0.0], [0.0,0.5,0.5]]


	def __init__(self, file_path=None, supercell_dimensions=None, lattice=None, species_list=None):
		sites = None
		if not file_path:
			sites = Perovskite.generate_perfect_site_collection(supercell_dimensions, species_list)


		super(Perovskite, self).__init__(file_path, lattice, sites)

		self.verify_is_perovskite()




	def verify_is_perovskite(self):
		if len(self.sites) % 5 != 0:
			raise Exception("Perovskite number of sites must be divisible by 5")
		elif len(self.sites.get_species_list()) != 3:
			raise Exception("Perovskite must have exactly three types of species")

		species_counts = self.sites.get_species_count_list()
		if species_counts[0]/species_counts[1] != 1.0 or species_counts[2]/species_counts[0] != 3.0:
			raise Exception("Perovskite ABO3 atom ratios not 1:1:3")


	@staticmethod
	def generate_perfect_site_collection(supercell_dimensions, species_list):
		"""Returns site collection with perfect perovskite direct coordinates

		See research slides for conventions on order of sites
		"""
		sites = SiteCollection()
		atom_types = species_list + [species_list[2], species_list[2]]

		for nz in range(supercell_dimensions[2]):
			for ny in range(supercell_dimensions[1]):
				for nx in range(supercell_dimensions[0]):
					n_list = [nx,ny,nz]

					for atom_index in range(5):
						position_list = [0.0, 0.0, 0.0]

						for i in range(3):
							offset = Perovskite.position_offsets[atom_index][i] / (1.0*supercell_dimensions[i])
							position_list[i] = (1.0*n_list[i]) / (1.0*supercell_dimensions[i]) + offset

						sites.append(Site({'position':position_list, 'coordinate_mode':'Direct', 'type':atom_types[atom_index]}))

		return sites