

from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.workflow.vasp_run_set import VaspRunSet
from fpctoolkit.workflow.flexible_parameter_list import ParameterList

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

	To have wavecars copied and used in the relaxation chain to increase performance, include WAVECAR in the
	incar modifications. 
	"""


	def __init__(self, path, initial_structure=None, external_relaxation_count=2, incar_modifications_list=None, kpoint_subdivisions_lists=None, kpoint_schemes_list=None, verbose=True):
		
		self.path = Path.clean(path)
		self.verbose = verbose
		self.run_count = 0 #how many runs have been initiated

		if external_relaxation_count < 0:
			raise Exception("Must have one or more external relaxations")

		self.external_relaxation_count = external_relaxation_count
		self.kpoint_schemes = ParameterList(kpoint_schemes_list)
		self.incar_modifiers

		self.vasp_run_list = []

		if Path.exists(self.path) and not Path.is_empty(self.path):
			#self.path is a non-empty directory. See if there's an old relaxation to load
			if Path.exists(self.get_save_path()):
				self.load()
			else: #Directory has files in it but no saved VaspRelaxation. This case is not yet supported
				raise Exception("Files present in relaxation directory but no run to load. Not yet supported.")
		else: #self.path is either an empty directory or does not exist
			Path.make(self.path)

	def create_next_run(self):
		run_path = self.get_next_run_path()

		kpoints = Kpoints(scheme_string=self.kpoint_schemes[self.run_count], subdivisions_list=base_kpoints_subdivisions_list)
		incar = IncarMaker.get_static_incar({'ediff':base_ediff, 'encut':encut})
		input_set = VaspInputSet(base_structure, kpoints, incar)

		vasp_run = VaspRun(run_path, input_set=input_set, verbose=self.verbose)
		self.run_count += 1

	def update(self):

		if self.run_count == 0 or self.get_current_vasp_run.complete:
			self.create_next_run()


		#if wavecar exists, make sure it is copied over

	def load(self):
		pass

	def get_next_run_path(self):
		return self.get_extended_path(self.get_next_run_path_basename)

	def get_next_run_path_basename(self):
		"""
		Returns relax_1 if no relaxes, returns relax_4 if three other relaxes exist, 
		returns static if self.run_count == self.external_relaxation_count
		"""

		if self.run_count == self.external_relaxation_count:
			return 'static'
		else:
			return 'relax_' + str(self.run_count + 1)

	def get_current_run_path(self):
		return self.get_extended_path(self.get_current_run_path_basename)

	def get_current_run_path_basename(self):
		if self.run_count == self.external_relaxation_count:
			return 'static'
		else:
			return 'relax_' + str(self.run_count)


	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)

	def get_save_path(self):
		return self.get_extended_path(".relaxation_pickle")

	def get_current_vasp_run(self):
		return self.vasp_run_list[self.run_count]


