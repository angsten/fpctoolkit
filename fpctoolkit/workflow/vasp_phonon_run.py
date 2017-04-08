#from fpctoolkit.workflow.vasp_phonon_run import VaspPhononRun

from phonopy import Phonopy
from phonopy.interface.vasp import read_vasp, write_vasp
from phonopy.interface.vasp import parse_set_of_forces
from phonopy.file_IO import parse_FORCE_SETS, parse_BORN
import numpy as np

from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.workflow.vasp_run_set import VaspRunSet
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.structure.structure import Structure
from fpctoolkit.io.file import File
import fpctoolkit.util.phonopy_interface.phonopy_utility as phonopy_utility

class VaspPhononRun(VaspRunSet):

	def __init__(self, path, initial_structure, phonopy_inputs_dictionary, vasp_run_inputs_dictionary):
		"""
		path holds the main path of the calculation sets

		initial_structure should be some small Structure instance for which one wishes to calculate phonons

		phonopy_inputs should be a dictionary that looks like:

		phonopy_inputs_dictionary = {
			'supercell_dimensions': [2, 2, 2],
			'symprec': 0.001,
			'displacement_distance': 0.01
			...
		}

		vasp_run_inputs_dictionary should be a dictionary that looks like:

		vasp_run_inputs_dictionary = {
			'kpoint_scheme': 'Monkhorst',
			'kpoint_subdivisions_list': [4, 4, 4]
		}
		"""

		self.path = path
		self.initial_structure = initial_structure
		self.phonopy_inputs = phonopy_inputs_dictionary
		self.vasp_run_inputs = vasp_run_inputs_dictionary
		self.phonon = None #holds the phonopy Phonopy class instance once initialized


		Path.make(path)


		self.initialize_phonon()


		####temp code#####
		symmetry = self.phonon.get_symmetry()
		print "Space group of initial primitive structure:", symmetry.get_international_table()
		####


		self.initialize_vasp_runs()

		self.update()

	def initialize_phonon(self):
		"""
		Initialize self.phonon so that it has a valid Phonopy instance and has displacements generated
		"""

		unit_cell_phonopy_structure = phonopy_utility.convert_structure_to_phonopy_atoms(self.initial_structure, self.get_extended_path("tmp_initial_phonon_structure_POSCAR"))
		supercell_dimensions_matrix = np.diag(self.phonopy_inputs['supercell_dimensions'])

		self.phonon = Phonopy(unitcell=unit_cell_phonopy_structure, supercell_matrix=supercell_dimensions_matrix, symprec=self.phonopy_inputs['symprec'])
		self.phonon.generate_displacements(distance=self.phonopy_inputs['displacement_distance'])

		#born = parse_BORN(phonon.get_primitive())
		#phonon.set_nac_params(born)


	def initialize_vasp_runs(self):
		distorted_structures_list = self.get_distorted_structures_list()

		for i, distorted_structure in enumerate(distorted_structures_list):
			run_path = self.get_extended_path(str(i))

			if not Path.exists(run_path):
				self.create_new_vasp_run(run_path, distorted_structure)


	def get_distorted_structures_list(self):
		supercells = self.phonon.get_supercells_with_displacements()

		distorted_structures_list = []
		for i in range(len(supercells)):
			distorted_structure = phonopy_utility.convert_phonopy_atoms_to_structure(supercells[i], self.initial_structure.get_species_list(), self.get_extended_path('./tmp_distorted_structure'))
			distorted_structures_list.append(distorted_structure)

		return distorted_structures_list


	def create_new_vasp_run(self, path, structure):
		kpoints = Kpoints(scheme_string=self.vasp_run_inputs['kpoint_scheme'], subdivisions_list=self.vasp_run_inputs['kpoint_subdivisions_list'])
		incar = IncarMaker.get_phonon_incar()

		input_set = VaspInputSet(structure, kpoints, incar)

		vasp_run = VaspRun(path=run_path, input_set=input_set)


	def update(self):
		if not self.complete:
			for vasp_run in self.vasp_run_list:
				vasp_run.update()
		else:
			self.set_force_constants()


	@property
	def vasp_run_list(self):
		vasp_run_list = []

		i = 0
		while Path.exists(self.get_extended_path(i)):
			run_path = self.get_extended_path(i)

			vasp_run_list.append(VaspRun(path=run_path))

		return vasp_run_list

	@property
	def complete(self):
		for vasp_run in self.vasp_run_list:
			if not vasp_run.complete:
				return False

		return True

	def set_force_constants(self):
		num_atoms = 40
		vasprun_xml_paths= [self.get_extended_path('vasprun_001.xml'), self.get_extended_path('vasprun_002.xml')]

		sets_of_forces = parse_set_of_forces(num_atoms=num_atoms, forces_filenames=vasprun_xml_paths)
		phonon.set_forces(sets_of_forces)

		phonon.produce_force_constants()


# def write_supercells_with_displacements(supercell,
#                                         cells_with_displacements):
#     write_vasp("SPOSCAR", supercell, direct=True)
#     for i, cell in enumerate(cells_with_displacements):
#         write_vasp('POSCAR-%03d' % (i + 1), cell, direct=True)

#     _write_magnetic_moments(supercell)
