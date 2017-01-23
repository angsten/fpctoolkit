from fpctoolkit.io.file import File
from fpctoolkit.io.poscar import Poscar

class Structure(object):
	
	def __init__(self, file_path=None, lattice=None, sites=None):

		if file_path: #load from file (only poscar supported for now)
			self.from_poscar_file(file_path)
		else:
			self.lattice = lattice
			self.sites = sites


	def from_poscar_file(self, file_path):
		pass

	def to_poscar_file(self, file_path):
		pass	