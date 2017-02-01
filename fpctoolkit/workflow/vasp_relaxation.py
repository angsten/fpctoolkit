import collections

from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.workflow.vasp_run_set import VaspRunSet
from fpctoolkit.workflow.flexible_parameter_list import ParameterList
from fpctoolkit.structure.structure import Structure

class VaspRelaxation(VaspRunSet):
	"""
	Collection of runs that form a relaxation.

	Contcar of last run in set always become poscar of next run.
	
	Incar and kpoints at each step can be custom specified. Modification
	lists do not have to be the same length as the number of vasp runs in
	the collection - if not then the default is to apply the last modification
	in the list to all future steps. See below for example input dictionary.

	The number of relaxation steps in for this run set is fixed - if run_count is
	4, then four external relaxations (isif = 3) will be performed before running a static (5 runs total).

	If external_relaxation_count == 0, then only a static is performed

	To not have wavecars copied and used in the relaxation chain to increase performance, include WAVECAR=Flase in the
	incar modifications. If wavecar exists in previous relax step's output, it will be copied to next step.
	
	Input dicitonary should look something like:
	{
		'external_relaxation_count': 4		
		'kpoint_schemes_list': ['Gamma'],
		'kpoint_subdivisions_lists': [[1, 1, 1], [1, 1, 2], [2, 2, 4]],
		'ediff': [0.001, 0.00001, 0.0000001],
		'encut': [200, 400, 600, 800],
		'isif' : [21, 33, 111]
		#any other incar parameters as a list
	}

	"""


	def __init__(self, path, initial_structure=None, external_relaxation_count=2, input_dictionary=None, incar_modifications_list=None, kpoint_subdivisions_lists=None, kpoint_schemes_list=None, verbose=True):
		
		self.path = Path.clean(path)
		self.verbose = verbose
		self.run_count = 0 #how many runs have been initiated

		if external_relaxation_count < 0:
			raise Exception("Must have one or more external relaxations")

		self.initial_structure = initial_structure
		self.external_relaxation_count = input_dictionary.pop('external_relaxation_count')
		self.kpoint_schemes = ParameterList(input_dictionary.pop('kpoint_schemes_list'))
		self.kpoint_subdivisions_lists = ParameterList(input_dictionary.pop('kpoint_subdivisions_lists'))


		self.incar_modifier_lists_dictionary = {}
		for key, value in input_dictionary.items():
			if not isinstance(value, collections.Sequence):
				raise Exception("Incar modifier lists in input dictionary must be given as sequences")
			else:
				self.incar_modifier_lists_dictionary[key] = ParameterList(value)


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

		structure = self.get_next_structure()
		kpoints = Kpoints(scheme_string=self.kpoint_schemes[self.run_count], subdivisions_list=self.kpoint_subdivisions_lists[self.run_count])

		incar_modification_dict = {} #will look like {'ediff':base_ediff, 'encut':encut, ...}
		for key, value_list in self.incar_modifier_lists_dictionary:
			incar_modification_dict[key] = value_list[self.run_count]

		if self.run_count < external_relaxation_count:
			incar = IncarMaker.get_external_relaxation_incar(incar_modification_dict)
		else:
			incar = IncarMaker.get_static_incar(incar_modification_dict)

		input_set = VaspInputSet(structure, kpoints, incar)

		#if wavecar exists in current relax run, make sure it is copied over to next run
		self.copy_wavecar_to_next_run

		vasp_run = VaspRun(run_path, input_set=input_set, verbose=self.verbose)
		self.run_count += 1

	def update(self):

		if self.run_count == 0 or self.get_current_vasp_run().complete:
			self.create_next_run()


		

	def load(self):
		pass

	def get_next_structure(self):
		"""If first relax, return self.initial_structure, else, get the contcar from the current run"""

		if self.run_count == 0:
			return self.initial_structure

		current_contcar_path = Path.join(self.get_current_run_path, 'CONTCAR')

		if not Path.exists(current_contcar_path):
			raise Exception("Method get_next_structure called, but Contcar for current run doesn't exist")
		elif not self.get_current_vasp_run().complete:
			raise Exception("Method get_next_structure called, but current run is not yet complete")

		return Structure(current_contcar_path)

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


