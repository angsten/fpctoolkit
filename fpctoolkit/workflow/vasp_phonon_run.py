#from fpctoolkit.workflow.vasp_phonon_run import VaspPhononRun

from phonopy import Phonopy
from phonopy.interface.vasp import read_vasp, write_vasp
from phonopy.interface.vasp import parse_set_of_forces
from phonopy.file_IO import parse_FORCE_SETS, parse_BORN
import numpy as np

from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_run_set import VaspRunSet
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.structure.structure import Structure
from fpctoolkit.io.file import File

class VaspPhononRun(VaspRunSet):

	def __init__(self, path, initial_structure):
		self.path = path

		Path.make(path)

		initial_poscar_path = self.get_extended_path("initial_phonon_structure_POSCAR")

		initial_structure.to_poscar_file_path(initial_poscar_path)

		primitive_structure = read_vasp(initial_poscar_path)
		supercell_dimensions_matrix = np.diag([2, 2, 2])
		symprec = 0.001

		displacement_distance = 0.01

		# Initialize phonon. Supercell matrix has to have the shape of (3, 3)
		phonon = Phonopy(unitcell=primitive_structure, supercell_matrix=supercell_dimensions_matrix, symprec=symprec)

		symmetry = phonon.get_symmetry() #symprec=1e-5, angle_tolerance=-1.0
		print "Space group:", symmetry.get_international_table()

		phonon.generate_displacements(distance=displacement_distance)
		supercells = phonon.get_supercells_with_displacements()



		distorted_structures_list = []
		for i in range(len(supercells)):
			distorted_structure_path = self.get_extended_path('./distorted_structure_'+str(i))

			write_vasp(distorted_structure_path, supercells[i])

			distorted_structure_poscar_file = File(distorted_structure_path)
			distorted_structure_poscar_file.insert(5, " ".join(initial_structure.get_species_list())) #phonopy uses bad poscar format
			distorted_structure_poscar_file.write_to_path()

			distorted_structures_list.append(Structure(distorted_structure_path))



		kpoint_scheme = 'Monkhorst'
		kpoint_subdivisions_list = [4, 4, 4]

		for i, distorted_structure in enumerate(distorted_structures_list):
			run_path = self.get_extended_path(str(i))

			if not Path.exists(run_path):
				structure = distorted_structure
				kpoints = Kpoints(scheme_string=kpoint_scheme, subdivisions_list=kpoint_subdivisions_list)
				incar = IncarMaker.get_phonon_incar()

				input_set = VaspInputSet(structure, kpoints, incar, submission_script_file=submission_script_file)

				vasp_run = VaspRun(path=run_path, input_set=input_set)

			vasp_run.update()







		#born = parse_BORN(phonon.get_primitive())
		#phonon.set_nac_params(born)


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
