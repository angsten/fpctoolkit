#from fpctoolkit.workflow.vasp_phonon import VaspPhonon

import numpy as np

from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.workflow.vasp_run_set import VaspRunSet
from fpctoolkit.workflow.vasp_forces_run_set import VaspForcesRunSet
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.structure.structure import Structure
from fpctoolkit.io.file import File
import fpctoolkit.util.phonopy_interface.phonopy_utility as phonopy_utility

class VaspPhonon(VaspRunSet):
	"""
	Represents a phonon run in vasp built on the phonopy finite differences framework. 
	This class takes as input an initial structure and parameters for the static force calculations
	as well as phonopy parameters.
	"""

	def __init__(self, path, initial_structure, phonopy_inputs_dictionary, vasp_run_inputs_dictionary, re_optimize_initial_structure=False):
		"""
		path holds the main path of the calculation sets

		initial_structure should be some small Structure instance for which one wishes to calculate phonons

		phonopy_inputs should be a dictionary that looks like:

		phonopy_inputs_dictionary = {
			'supercell_dimensions': [2, 2, 2],
			'symprec': 0.001,
			'displacement_distance': 0.01,
			'nac': True
			...
		}

		vasp_run_inputs_dictionary should be a dictionary that looks like:

		vasp_run_inputs_dictionary = {
			'kpoint_scheme': 'Monkhorst',
			'kpoint_subdivisions_list': [4, 4, 4] #***This is the kpoints of the supercell, not the primitive cell!!!***
		}
		"""

		self.path = path
		self.initial_structure = initial_structure if (not re_optimize_initial_structure) else None
		self.phonopy_inputs = phonopy_inputs_dictionary
		self.vasp_run_inputs = vasp_run_inputs_dictionary
		self.forces_run_set = None #holds set of force calculations on distorted structures
		self.lepsilon_calculation = None #calculates dielectric tensor and born effective charge if nac is needed


		Path.make(path)

		self.initialize_forces_run_set()

		if self.has_nac():
			self.initialize_vasp_lepsilon_calculation()

		self.update()


	def initialize_forces_run_set(self):
		"""
		Creates the set of force calculation vasp runs on the phonopy generated list of distorted structures.
		"""

		self.forces_run_set = VaspForcesRunSet(path=self.get_forces_run_set_path(), structures_list=self.get_distorted_structures_list(), 
			vasp_run_inputs_dictionary=self.vasp_run_inputs, wavecar_path=None)


	def get_distorted_structures_list(self):
		"""
		Returns list of Structure instances containing the distorted structures determined as necessary to calculate the forces of by phonopy.
		"""

		#########make sure we're using proper initial structure if there was reoptimization#####################################################################################

		return phonopy_utility.get_distorted_structures_list(initial_structure=self.initial_structure, phonopy_inputs=self.phonopy_inputs, temporary_directory_path=self.path)


	def initialize_vasp_lepsilon_calculation(self):
		"""
		Sets up a run for the calculation of dielectric and born effective charge tensors. This is necessary if the Non-Analytical correction is used (for polar materials).
		"""

		kpoints = Kpoints(scheme_string=self.vasp_run_inputs['kpoint_scheme'], subdivisions_list=[self.vasp_run_inputs['kpoint_subdivisions_list'][i]*self.phonopy_inputs['supercell_dimensions'][i] for i in range(3)])
		incar = IncarMaker.get_lepsilon_incar()

		input_set = VaspInputSet(self.initial_structure, kpoints, incar, auto_change_npar=False)

		self.lepsilon_calculation = VaspRun(path=self.get_lepsion_calculation_path(), input_set=input_set)



	def update(self):
		"""
		Runs update on all force calculations (and potentially the lepsilon calculation) until they are all complete. 
		Once they are all complete, the force constants are generated and written to file, completing the phonon calculation.
		"""

		if not self.complete:
			self.forces_run_set.update()

			if self.has_nac():
				self.lepsilon_calculation.update()

		else:
			self.write_initial_structure()
			self.write_force_constants()

			if self.has_nac()
				self.write_born_file()



	@property
	def complete(self):
		if not self.forces_run_set.complete:
			return False

		if self.has_nac() and not self.lepsilon_calculation.complete:
			return False

		return True



	def has_nac(self):
		return self.phonopy_inputs.has_key('nac') and self.phonopy_inputs['nac']



	def get_initial_structure_path(self):
		return self.get_extended_path('initial_structure')

	def get_force_constants_path(self):
		return self.get_extended_path('FORCE_CONSTANTS')

	def get_born_path(self):
		return self.get_extended_path('BORN')

	def get_lepsion_calculation_path(self):
		return self.get_extended_path('lepsilon_calculation')

	def get_forces_run_set_path(self):
		return self.get_extended_path('force_calculations')



	def write_initial_structure(self):
		"""
		Writes the initial structure used to generate displacements to a poscar file.
		"""

		#######make sure this is reoptimized structure
		self.initial_structure.to_poscar_file_path(self.get_initial_structure_path())

	def write_force_constants(self):
		"""
		Writes the calculated force constants to file.
		"""

		phonopy_utility.write_force_constants_to_file_path(initial_structure=self.initial_structure, phonopy_intputs=self.phonopy_inputs, 
			temporary_directory_path=temporary_directory_path, vasp_xml_file_paths_list=self.forces_run_set.get_xml_file_paths_list(), file_path=self.get_force_constants_path())


	def write_born_file(self):
		"""
		Writes born file necessary for NAC to file.
		"""

		if self.has_nac():
			dielectric_tensor = self.lepsilon_calculation.outcar.get_dielectric_tensor()
			born_effective_charge_tensor = self.lepsilon_calculation.outcar.get_born_effective_charge_tensor()

			write_born_file(initial_structure=self.initial_structure, phonopy_inputs=self.phonopy_inputs, temporary_directory_path=self.path, 
				dielectric_tensor=dielectric_tensor, born_effective_charge_tensor=born_effective_charge_tensor, file_path=self.get_born_path())




	# def set_force_constants(self):
	# 	sets_of_forces = parse_set_of_forces(num_atoms=self.get_supercell_atom_count(), forces_filenames=self.forces_run_set.get_xml_file_paths_list())

	# 	self.phonon.produce_force_constants(sets_of_forces)

	# 	#print self.phonon.get_frequencies_with_eigenvectors([0.0, 0.0, 0.05])

	# 	if self.has_nac():
	# 		born_path = self.get_extended_path('BORN')

	# 		dielectric_tensor = self.lepsilon_calculation.outcar.get_dielectric_tensor()
	# 		born_effective_charge_tensor = self.lepsilon_calculation.outcar.get_born_effective_charge_tensor()

	# 		symm = Symmetry(cell=self.phonon.get_primitive(), symprec=self.phonopy_inputs['symprec'])
	# 		independent_atom_indices_list = symm.get_independent_atoms()

	# 		phonopy_utility.write_born_file(born_file_path=born_path, dielectric_tensor=dielectric_tensor, 
	# 			born_effective_charge_tensor=born_effective_charge_tensor, independent_atom_indices_list=independent_atom_indices_list)

	# 		nac_params = parse_BORN(self.phonon.get_primitive(), filename=born_path)
	# 		self.phonon.set_nac_params(nac_params)

	# 	#print self.phonon.get_frequencies_with_eigenvectors([0.0, 0.0, 0.05])