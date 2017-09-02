#from fpctoolkit.workflow.vasp_hybrid_dos_run_set import VaspHybridDosRunSet

import collections
import copy

from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.workflow.vasp_run_set import VaspRunSet
from fpctoolkit.data_structures.parameter_list import ParameterList
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.structure.structure import Structure
from fpctoolkit.util.path import Path
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.util.queue_adapter import QueueAdapter, QueueStatus
from fpctoolkit.io.file import File
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation

class VaspHybridDosRunSet(VaspRunSet):
	"""
	Collection of runs that form a hybrid dos calculation

	The general workflow is:
	1. Relax (internally, externally, or skip and use expt structure) using PBE GGA - to skip set external_relaxation_count to zero
	2. Run normal GGA static calculation at normal kpoints with lwave on
	3. Run HSE06 calculation using this wavecar with lwave on using guassian smearing with prefock = fast and NKRED = 2 and algo = all time = 0.4
	4. Run HSE06 from the above wavecar with lwave and lcharge on using tetrahedral smearing with prefock = Normal and no NKRED set and IALGO = 53; TIME = 0.4
	5. Rerun HSE06 at desired higher kpoints with above chargecar, ICHARGE = 11, lorbit = 11, and all other same incar settings above

	"""

	def __init__(self, path, initial_structure=None, relaxation_input_dictionary=None, extra_dos_inputs=None):
		"""
		Input dicitonary should look something like:
		{
			'external_relaxation_count': 4,
			'kpoint_schemes_list': ['Gamma'],
			'kpoint_subdivisions_lists': [[1, 1, 1], [1, 1, 2], [2, 2, 4]],
			'submission_script_modification_keys_list': ['100', 'standard', 'standard_gamma'], #optional - will default to whatever queue adapter gives
			'submission_node_count_list': [1, 2],
			'ediff': [0.001, 0.00001, 0.0000001],
			'encut': [200, 400, 600, 800],
			'isif' : [5, 2, 3],
			'calculation_type': 'gga' #must be gga in this case
			#any other incar parameters with value as a list
		}

		extra_dos_inputs is optional and should look like:
		{
			HFSCREEN = 0.2 # sets the type of hybid - can give params for pbe0 here too
			NEDOS = 4001
			'kpoint_schemes_list': ['Gamma'],
			'kpoint_subdivisions_lists': [[2, 2, 4]], #for enhanced kpoints - can be up to three for each stage of the dos
			any other incar params for just dos part
		}

		If no relaxation_input_dictionary is provided, this class will attempt to load a saved pickled instance.
		"""

		self.path = Path.expand(path)
		self.relaxation_path = self.get_extended_path('relaxation')
		self.dos_path = self.get_extended_path('dos')
		self.extra_dos_inputs = extra_dos_inputs
		self.dos_runs_list = []

		if 'calculation_type' not in relaxation_input_dictionary or relaxation_input_dictionary['calculation_type'] != 'gga':
			raise Exception("Calculation type must be gga for hybrid calculations")

		if not relaxation_input_dictionary:
			self.load()
		else:

			Path.make(self.path)

			relaxation_input_dictionary['static_lwave'] = True
			self.relaxation = VaspRelaxation(path=self.relaxation_path, initial_structure=initial_structure, input_dictionary=relaxation_input_dictionary)
			self.save()

	def get_current_dos_count(self):
		if Path.exists(Path.join(self.dos_path, 'hybrid_electronic_optimization_3')):
			return 3 
		elif Path.exists(Path.join(self.dos_path, 'hybrid_electronic_optimization_2')):
			return 2
		elif Path.exists(Path.join(self.dos_path, 'hybrid_electronic_optimization_1')):
			return 1
		else:
			return 0

	def update(self):
		if not self.relaxation.complete:
			self.relaxation.update()
		else:
			Path.make(self.dos_path)

			dos_runs_count = self.get_current_dos_count()

			incar_modifications = {}
			for key, value_list in self.relaxation.incar_modifier_lists_dictionary:
				incar_modifications[key] = value_list[1000]

			incar = IncarMaker.get_static_incar(incar_modifications)

			if 'submission_node_count' in self.extra_dos_inputs:
				node_count = self.extra_dos_inputs.pop('submission_node_count')
			else:
				node_count = None

			structure = self.relaxation.final_structure
			kpoint_schemes =  ParameterList(self.extra_dos_inputs.pop('kpoint_schemes_list'))
			kpoint_subdivisions_lists = ParameterList(self.extra_dos_inputs.pop('kpoint_subdivisions_lists'))

			kpoints = Kpoints(scheme_string=kpoint_schemes[dos_runs_count], subdivisions_list=kpoint_subdivisions_lists[dos_runs_count])
			incar = IncarMaker.get_static_incar(incar_modifications)

			for key, value in self.extra_dos_inputs.items():
				incar[key] = value

			if node_count != None:
				input_set.set_node_count(node_count)

			incar['lhfcalc'] = True
			incar['hfscreen'] = 0.2
			incar['lorbit'] = 11

			chargecar_path = None


			if dos_runs_count == 0:
				run_path = path.join(self.dos_path, 'hybrid_electronic_optimization_1')
				Path.make(run_path)

				wavecar_path = Path.join(self.relaxation.path, 'static', 'WAVECAR')

				incar['algo'] = 'All'
				incar['time'] = 0.4
				incar['precfock'] = 'Fast'
				incar['nkred'] = 2
				incar['ismear'] = 0
				incar['sigma'] = 0.02
				incar['lwave'] = True

			elif dos_runs_count == 1 and self.dos_runs_list[-1].complete:
				run_path = path.join(self.dos_path, 'hybrid_electronic_optimization_2')
				Path.make(run_path)

				wavecar_path = Path.join(self.dos_path, 'hybrid_electronic_optimization_1', 'WAVECAR')

				incar['ialgo'] = 53
				incar['time'] = 0.4
				incar['precfock'] = 'Fast'
				incar['nkred'] = 2
				incar['ismear'] = -5
				incar['sigma'] = 0.02
				incar['lwave'] = True
				incar['lcharg'] = True

			elif dos_runs_count == 2 and self.dos_runs_list[-1].complete:
				run_path = path.join(self.dos_path, 'hybrid_electronic_optimization_3')
				Path.make(run_path)

				wavecar_path = Path.join(self.dos_path, 'hybrid_electronic_optimization_2', 'WAVECAR')
				chargecar_path = Path.join(self.dos_path, 'hybrid_electronic_optimization_2', 'CHARGECAR')

				incar['ialgo'] = 53
				incar['time'] = 0.4
				incar['precfock'] = 'Fast'
				incar['nkred'] = 2
				incar['ismear'] = -5
				incar['sigma'] = 0.02
				incar['lwave'] = True
				incar['lcharg'] = True
				incar['icharge'] = 11

	

			input_set = VaspInputSet(structure, kpoints, incar, calculation_type='gga')

			current_dos_run = VaspRun(path=run_path, input_set=input_set, wavecar_path=wavecar_path, chargecar_path = None)

			current_dos_run.update()




	# @property
	# def complete(self):
	# 	#print "in complete" + str(self.get_current_vasp_run()) + str(self.get_current_vasp_run().complete)
	# 	return (self.run_count == self.external_relaxation_count + 1) and self.get_current_vasp_run().complete


	# def delete_non_static_wavecars(self):
	# 	for i, vasp_run in enumerate(self.vasp_run_list):
	# 		if i < len(self.vasp_run_list)-1:
	# 			vasp_run.delete_wavecar_if_complete()


