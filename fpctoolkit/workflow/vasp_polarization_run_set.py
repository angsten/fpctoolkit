#from fpctoolkit.workflow.vasp_polarization_run_set import VaspPolarizationRunSet

from fpctoolkit.io.file import File
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.potcar import Potcar
from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.io.vasp.incar import Incar
from fpctoolkit.structure.structure import Structure
from fpctoolkit.io.vasp.outcar import Outcar
from fpctoolkit.util.path import Path
from fpctoolkit.util.queue_adapter import QueueAdapter, QueueStatus
import fpctoolkit.util.string_util as su

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
		"""

		Structure.validate(reference_structure)
		Structure.validate(distorted_structure)


		if not reference_structure.lattice.equals(distorted_structure.lattice):
			raise Exception("Warning: It's very difficult to interpret polarization results when the lattices of the reference and distorted structures are not equal. This is likely an error.", reference_structure.lattice, distorted_structure.lattice)


		self.path = path
		self.reference_structure = reference_structure
		self.distorted_structure = distorted_structure
		self.vasp_run_inputs = copy.deepcopy(vasp_run_inputs_dictionary)

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

		input_set = VaspInputSet(structure, kpoints, incar, auto_change_lreal=('lreal' not in run_inputs), auto_change_npar=('npar' not in run_inputs))


		if node_count != None:
			input_set.set_node_count(node_count)

			# if 'npar' not in run_inputs:
			# 	input_set.set_npar_from_number_of_cores()

		vasp_run = VaspRun(path=path, input_set=input_set)

	def update(self):
		"""
		Runs update on all force calculations until they are all complete. 
		"""

		if not self.complete:
			for vasp_run in self.vasp_run_list:
				vasp_run.update()

	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)