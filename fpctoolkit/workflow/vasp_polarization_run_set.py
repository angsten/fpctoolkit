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