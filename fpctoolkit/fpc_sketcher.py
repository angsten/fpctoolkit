

from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.potcar import Potcar
from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.io.vasp.incar import Incar
from fpctoolkit.util.path import Path
from fpctoolkit.io.file import File
from fpctoolkit.structure.site import Site
from fpctoolkit.structure.lattice import Lattice
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.structure.site_collection import SiteCollection
from fpctoolkit.io.vasp.outcar import Outcar
from fpctoolkit.workflow.vasp_run import VaspRun
#import fpctoolkit.util.string_util as su


class self_c:
	def __init__(self):
		data_path = ""

	def assertEqual(self, left_arg, right_arg = None):
		if not right_arg:
			print left_arg
		else:
			print left_arg == right_arg

	def assertTrue(self, cond):
		print cond

def get_string(printed):
	out_str = '"'
	for line in printed:
		out_str += line + r'\n'
	return out_str + '"'

self = self_c()

#self.data_path = "C:/Users/Tom/Documents/Berkeley/research/scripts/fpctoolkit/fpctoolkit/structure/tests/data_structure/"
self.data_path = "C:\Users\Tom\Documents\Coding\python_work\workflow_test"

# convergence_base_path = Path.clean(self.data_path)

# Path.remove(convergence_base_path)

# structure = Perovskite(supercell_dimensions = [2, 2, 2], lattice=[[4.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 4.0]], species_list=['K', 'V', 'O'])
# incar = Incar()

# incar['IBRION'] = -1
# incar['NSW'] = 0
# incar['ISMEAR'] = 0
# incar['SIGMA'] = 0.01
# incar['LREAL'] = False
# incar['LWAVE'] = False
# incar['LCHARG'] = False
# incar['NPAR'] = 2
# incar['PREC'] = 'Accurate'
# incar['EDIFF'] = 0.00001
# incar['ENCUT'] = 400
# incar['NELMIN'] = 4

# kpoints = Kpoints(scheme_string='Monkhorst', subdivisions_list=[2, 2, 2])


# vasp_run = VaspRun(convergence_base_path, structure, incar, kpoints, None)

