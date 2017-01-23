from fpctoolkit.io.file import File
from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.structure.site import Site
from fpctoolkit.structure.lattice import Lattice

class Structure(object):
	"""Abstract crystal structure class.

	Holds 2D array for lattice and a list of sites (see Site calss)
	Compatible with poscar file class only for now.
	"""
	def __init__(self, file_path=None, lattice=None, sites=None):

		if file_path: #load from file (only poscar supported for now)
			self.from_poscar_file(file_path)
		else:
			self.lattice = Lattice(lattice)
			self.sites = sites

	def __str__(self):
		return str(self.lattice) + "\n".join(str(site) for site in self.sites)


	def from_poscar_file(self, file_path):
		poscar = Poscar(file_path)
		self.lattice = Lattice(poscar.lattice)
		self.sites = []

		species_index = 0
		for i, specie in enumerate(poscar.species_list):
			for j in range(poscar.species_count_list[i]):
				new_site = Site()
				new_site['coordinate_mode'] = poscar.coordinate_mode
				new_site['position'] = poscar.coordinates[species_index]
				new_site['type'] = specie

				self.sites.append(new_site)

				species_index += 1


	def to_poscar_file(self, file_path):
		pass