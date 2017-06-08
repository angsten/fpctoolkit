#from fpctoolkit.workflow.vasp_polarization_run_set import VaspPolarizationRunSet

import copy

from fpctoolkit.io.file import File
from fpctoolkit.structure.structure import Structure
from fpctoolkit.io.vasp.outcar import Outcar
from fpctoolkit.util.path import Path
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.workflow.vasp_run import VaspRun

class VaspPolarizationRunSet(object):
	"""
	Class wrapper for vasp polarization calculations.

	This uses the Berry phase approach to calculate the change in total polarization (sum of ionic and electronic) in going from a reference structure to a distorted structure (with the same lattice, only atomic positions 
	should be different).

	The shorted polarization vector is always found, because polarization is defined to be unique within modulo (e*R)/omega, where R can be any sum of lattice vectors, and omega is the cell volume. This means this run set
	may not give the correct polarization vector if the true vector exceeds this fundamental vector in length (but this is rare).
	"""

	def __init__(self, path, reference_structure, distorted_structure, vasp_run_inputs_dictionary):
		"""
		reference_structure should be a Structure instance with the same lattice as distorted structure. Usually this reference is chosen to be centrosymmetry (like ideal perovskite) so that 
		absolute polarizations of the distorted structure can be caluclated.

		distorted_structure should be a Structure instance with the same lattice as the reference structure, but some of the atoms shifted to cause a change in polarization.

		vasp_run_inputs_dictionary should look like:

		vasp_run_inputs_dictionary = {
			'kpoint_scheme': 'Monkhorst',
			'kpoint_subdivisions_list': [4, 4, 4],
			'encut': 800,
			'npar': 1 (optional)
		}

		"""

		Structure.validate(reference_structure)
		Structure.validate(distorted_structure)


		if not reference_structure.lattice.equals(distorted_structure.lattice):
			raise Exception("Warning: It's very difficult to interpret polarization results when the lattices of the reference and distorted structures are not equal. This is likely an error.", reference_structure.lattice, distorted_structure.lattice)


		self.path = path
		self.reference_structure = reference_structure
		self.distorted_structure = distorted_structure
		self.vasp_run_inputs = copy.deepcopy(vasp_run_inputs_dictionary)
		self.vasp_run_list = []

		Path.make(path)

		self.initialize_vasp_runs()


	def initialize_vasp_runs(self):
		"""
		Creates two vasp runs - one for the reference structure polarization calculation, and one for the distorted structure polarization calculation.
		"""

		reference_polarization_path = self.get_extended_path('reference_polarization')
		distorted_polarization_path = self.get_extended_path('distorted_polarization')

		if not Path.exists(reference_polarization_path):
			self.create_new_vasp_run(reference_polarization_path, self.reference_structure)

		if not Path.exists(distorted_polarization_path):
			self.create_new_vasp_run(distorted_polarization_path, self.distorted_structure)		


	def create_new_vasp_run(self, path, structure):
		"""
		Creates a polarization calculation at path using structure as the initial structure and self.vasp_run_inputs as the run inputs.
		"""

		run_inputs = copy.deepcopy(self.vasp_run_inputs)

		if 'submission_node_count' in run_inputs:
			node_count = run_inputs.pop('submission_node_count')
		else:
			node_count = None

		kpoints = Kpoints(scheme_string=run_inputs.pop('kpoint_scheme'), subdivisions_list=run_inputs.pop('kpoint_subdivisions_list'))
		incar = IncarMaker.get_lcalcpol_incar(run_inputs)

		input_set = VaspInputSet(structure, kpoints, incar, auto_change_lreal=('lreal' not in run_inputs), auto_change_npar=False)


		if node_count != None:
			input_set.set_node_count(node_count)

			# if 'npar' not in run_inputs:
			# 	input_set.set_npar_from_number_of_cores()

		vasp_run = VaspRun(path=path, input_set=input_set)

		self.vasp_run_list.append(vasp_run)

	def update(self):
		"""
		Runs update on all force calculations until they are all complete. 
		"""

		if not self.complete:
			for vasp_run in self.vasp_run_list:
				vasp_run.update()


	def get_change_in_polarization(self):

		if not self.complete:
			return None

		cell_volume = self.reference_structure.get_volume() #in A^3
		lattice = self.reference_structure.lattice.to_np_array() #in Angstroms

		reference_polarization_vector = self.get_polarization(path=self.get_extended_path('reference_polarization')) #now holds reference ionic and electronic polarization in e*A
		distorted_polarization_vector = self.get_polarization(path=self.get_extended_path('distorted_polarization'))



		e = -1.6021766209*10**-19 #in Coulombs, negative because vasp outputs in e, not abs value of e
		angstroms_sq_per_meter_sq = 10**20
		conversion_factor = e*(1/cell_volume)*angstroms_sq_per_meter_sq

		total_polarization_vector = (distorted_polarization_vector - reference_polarization_vector)*conversion_factor

		search_range_minimum = -3
		search_range_maximum = 3
		minimum_polarization_magnitude = 1000000000
		minimum_polarization_vector = None

		for i in range(search_range_minimum, search_range_maximum):
			for j in range(search_range_minimum, search_range_maximum):
				for k in range(search_range_minimum,search_range_maximum):

					shift_vector = 2*(i*lattice[0] + j*lattice[1] + k*lattice[2])*conversion_factor #polarization defined within modulo eR/omega (factor of two works for non-spin-pol calcs only)

					shifted_total_polarization_vector = total_polarization_vector + shift_vector

					polarization_magnitude = np.linalg.norm(shifted_total_polarization_vector)

					if polarization_magnitude < minimum_polarization_magnitude:
						minimum_polarization_magnitude = polarization_magnitude
						minimum_polarization_vector = shifted_total_polarization_vector

		return minimum_polarization_vector



	def get_reference_polarization(self, path):
		"""
		Returns the polarization vector in e for the lcalcpol calculation at path
		"""

		outcar = Outcar(Path.join(path, 'OUTCAR'))

		polarization_vectors_list = outcar.get_ionic_and_electronic_polarization_vectors()

		ionic_polarization_vector = polarization_vectors_list[0]
		electronic_polarization_vector = polarization_vectors_list[1]

		return ionic_polarization_vector + electronic_polarization_vector



	@property
	def complete(self):
		for vasp_run in self.vasp_run_list:
			if not vasp_run.complete:
				return False

		return True

	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)