

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
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.io.vasp.incar_maker import IncarMaker
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
#self.data_path = "~/workflow_test/"

convergence_base_path = Path.clean(self.data_path)
Path.make(convergence_base_path)

base_kpoints_scheme = 'Monkhorst'
base_kpoints_subdivisions_list = [4, 4, 4]
base_encut = 800
base_ediff = 0.000001
base_structure = Perovskite(supercell_dimensions = [2, 2, 2], lattice=[[8.0, 0.0, 0.0], [0.0, 8.0, 0.0], [0.0, 0.0, 8.0]], species_list=['Ba', 'Ti', 'O'])

convergence_encuts_list = [500]

encut_convergence_set_path = Path.join(convergence_base_path, 'encut_convergence_set')
Path.make(encut_convergence_set_path)

for encut in convergence_encuts_list:
	run_path = Path.join(encut_convergence_set_path, str(encut))

	kpoints = Kpoints(scheme_string=base_kpoints_scheme, subdivisions_list=base_kpoints_subdivisions_list)
	incar = IncarMaker.get_static_incar({'ediff':base_ediff, 'encut':encut})
	input_set = VaspInputSet(base_structure, kpoints, incar)

	vasp_run = VaspRun(run_path, input_set=input_set)

	vasp_run.start()
	print vasp_run
