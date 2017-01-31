

from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.workflow.vasp_run_set import VaspRunSet
from fpctoolkit.workflow.flexible_parameter_list import FlexibleParameterList

class VaspRelaxation(VaspRunSet):
	"""
	Collection of runs that form a relaxation.

	Contcar of last run in set always become poscar of next run.
	Incar and kpoints at each step can be custom specified. Modification
	lists do not have to be the same length as the number of vasp runs in
	the collection - if not then the default is to apply that last modification
	in the list to all future steps.

	The number of relaxation steps in for this run set is fixed - if run_count is
	4, then four external relaxations (isif = 3) will be performed before running a static.

	If external_relaxation_count == 0, then only a static is performed
	"""


	def __init__(self, path, initial_structure=None, external_relaxation_count=2, use_wavecars=True, incar_modifications_list=None, kpoint_subdivisions_lists=None, kpoint_schemes=None, verbose=True):
		
		self.path = Path.clean(path)
		self.verbose = verbose

		if external_relaxation_count < 0:
			raise Exception("Must have one or more external relaxations")

		self.external_relaxation_count = external_relaxation_count
		self.use_wavecars = use_wavecars
		self.incar_modifiers

		self.vasp_run_list = []

		if Path.exists(self.path) and not Path.is_empty(self.path):
			#We're in a non-empty directory. See if there's an old relaxation to load
			if Path.exists(self.get_save_path()):
				self.load()
			else: #Directory has files in it but no saved VaspRelaxation. This case is not yet supported
				raise Exception("Files present in relaxation directory but no run to load. Not yet supported.")
		else:
			Path.make(self.path)

			self.log("Directory at run path did not exist or was empty. Created directory.")

			self.setup() #writes input files into self.path



	def start(self):
		run_path = Path.join(encut_convergence_set_path, str(encut))

		kpoints = Kpoints(scheme_string=base_kpoints_scheme, subdivisions_list=base_kpoints_subdivisions_list)
		incar = IncarMaker.get_static_incar({'ediff':base_ediff, 'encut':encut})
		input_set = VaspInputSet(base_structure, kpoints, incar)

		vasp_run = VaspRun(run_path, input_set=input_set)


	def update(self):

		if len(self.vasp_run_list) == 0:
			self.start()

	def load(self):
		pass

	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)

	def get_save_path(self):
		return self.get_extended_path(".relaxation_pickle")


