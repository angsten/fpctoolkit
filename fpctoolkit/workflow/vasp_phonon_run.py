#from fpctoolkit.workflow.vasp_phonon_run import VaspPhononRun

from phonopy import Phonopy
from phonopy.interface.vasp import read_vasp
from phonopy.file_IO import parse_FORCE_SETS, parse_BORN
import numpy as np

from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_run_set import VaspRunSet

class VaspPhononRun(VaspRunSet):

	def __init__(self, path, initial_structure):
		self.path = path

		Path.make(path)

		initial_poscar_path = self.get_extended_path("initial_phonon_structure_POSCAR")

		initial_structure.to_poscar_file_path(initial_poscar_path)

		primitive_structure = read_vasp(initial_poscar_path)
		supercell_dimensions_matrix = np.diag([2, 2, 2])

		# Initialize phonon. Supercell matrix has to have the shape of (3, 3)
		phonon = Phonopy(primitive_structure, supercell_dimensions_matrix)

		symmetry = phonon.get_symmetry()
		print "Space group:", symmetry.get_international_table()


