import collections
import cPickle

from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.workflow.vasp_run_set import VaspRunSet
from fpctoolkit.workflow.parameter_list import ParameterList
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.structure.structure import Structure
from fpctoolkit.util.path import Path
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet

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
		#any other incar parameters with value as a list
	}

	"""


	def __init__(self, path, initial_structure=None, input_dictionary=None, verbose=True):
		
		self.path = Path.clean(path)
		self.verbose = verbose
		self.run_count = 0 #how many runs have been initiated

		self.initial_structure = initial_structure
		self.external_relaxation_count = input_dictionary.pop('external_relaxation_count')
		self.kpoint_schemes = ParameterList(input_dictionary.pop('kpoint_schemes_list'))
		self.kpoint_subdivisions_lists = ParameterList(input_dictionary.pop('kpoint_subdivisions_lists'))

		if self.external_relaxation_count < 0:
			raise Exception("Must have one or more external relaxations")


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

		self.save()

	def create_next_run(self):
		run_path = self.get_next_run_path()

		structure = self.get_next_structure()
		kpoints = Kpoints(scheme_string=self.kpoint_schemes[self.run_count], subdivisions_list=self.kpoint_subdivisions_lists[self.run_count])
		incar = self.get_next_incar()

		input_set = VaspInputSet(structure, kpoints, incar)

		vasp_run = VaspRun(run_path, input_set=input_set, verbose=self.verbose, wavecar_path=self.get_wavecar_path())

		self.vasp_run_list.append(vasp_run)

		self.run_count += 1 #increment at end - this tracks how many runs have been created up to now

	def inner_update(self):

		if self.complete:
			return True
		elif self.run_count == 0 or self.get_current_vasp_run().complete:
			self.create_next_run()

		self.get_current_vasp_run().update()

		#delete all wavecars when finished or if True is returned

	def update(self):
		completed = self.inner_update()
		self.save()
		return completed

	@property
	def complete(self):
		return (self.run_count == self.external_relaxation_count + 1) and self.get_current_vasp_run().complete

	def get_next_incar(self):
		"""
		Returns the incar corresponding to the next run in the relaxation set
		"""

		incar_modifications_dict = {} #will look like {'ediff':base_ediff, 'encut':encut, ...}
		for key, value_list in self.incar_modifier_lists_dictionary.items():
			incar_modifications_dict[key] = value_list[self.run_count]

		if self.run_count < self.external_relaxation_count:
			incar = IncarMaker.get_external_relaxation_incar(incar_modifications_dict)
		else:
			incar = IncarMaker.get_static_incar(incar_modifications_dict)

		return incar
	
	def get_wavecar_path(self):
		"""
		If lwave of current run is true, returns path to wavecar of current run, else None
		"""
		if self.run_count == 0:
			return None

		current_run = self.get_current_vasp_run()
		if current_run.incar['lwave']:
			wavecar_path = current_run.get_extended_path('WAVECAR')

		return wavecar_path if Path.exists(wavecar_path) else None

	def get_next_structure(self):
		"""If first relax, return self.initial_structure, else, get the contcar from the current run"""

		if self.run_count == 0:
			return self.initial_structure

		current_contcar_path = self.get_current_vasp_run().get_extended_path('CONTCAR')
		print current_contcar_path
		if not Path.exists(current_contcar_path):
			raise Exception("Method get_next_structure called, but Contcar for current run doesn't exist")
		elif not self.get_current_vasp_run().complete:
			raise Exception("Method get_next_structure called, but current run is not yet complete")

		return Structure(current_contcar_path)

	def get_next_run_path(self):
		return self.get_extended_path(self.get_next_run_path_basename())

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
		return self.get_extended_path(self.get_current_run_path_basename())

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
		return self.vasp_run_list[self.run_count-1]

	def save(self):
		"""
		Saves class to pickled file at {self.path}/.relaxation_pickle

		Saves all attributes except vasp_run_list - this list is recreated
		later by saving all runs now and loading them later from the run directories. 
		"""

		save_path = self.get_save_path()

		save_dictionary = {key: value for key, value in self.__dict__.items() if not key == 'vasp_run_list'}

		file = open(save_path, 'w')
		file.write(cPickle.dumps(save_dictionary))
		file.close()

		for run in self.vasp_run_list:
			run.save()

	def load(self, load_path=None):
		previous_path = self.path
		previous_verbose = self.verbose

		if not load_path:
			load_path = self.get_save_path()

		if not Path.exists(load_path):
			self.log("Load file path does not exist: " + load_path, raise_exception=True)

		file = open(load_path, 'r')
		data_pickle = file.read()
		file.close()

		self.__dict__ = cPickle.loads(data_pickle)
		self.verbose = previous_verbose #so this can be overridden upon init
		self.path = previous_path #in case relaxation is moved

		saved_run_count = self.run_count

		self.vasp_run_list = []
		self.run_count = 0

		for count in range(saved_run_count):
			self.vasp_run_list.append(VaspRun(path=self.get_next_run_path()))

			self.run_count += 1