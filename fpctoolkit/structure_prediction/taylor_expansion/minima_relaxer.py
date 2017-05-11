#from fpctoolkit.structure_prediction.taylor_expansion.minima_relaxer import MinimaRelaxer

import copy
import numpy as np

from fpctoolkit.workflow.vasp_static_run_set import VaspStaticRunSet
from fpctoolkit.util.path import Path
from fpctoolkit.phonon.eigen_structure import EigenStructure



class MinimaRelaxer(object):
	"""
	Takes in a list of eigen_chromosomes that are the minima guesses from the taylor expansion and relaxes these guesses using full vasp relaxations.

	The relaxations are then sortable by energy, and one can see the change in the eigen_chromosomes in going from the guess to the relaxed structure
	"""

	def __init__(self, path, reference_structure, hessian, taylor_expansion, reference_completed_vasp_relaxation_run, vasp_run_inputs_dictionary, perturbation_magnitudes_dictionary):
		"""
		taylor_expansion should be an initialized TaylorExpansion instance with the appropriate terms.
		
		perturbation_magnitudes_dictionary should look like {'strain': 0.02, 'displacement': 0.01} with strain as fractional and displacement in angstroms

		vasp_run_inputs_dictionary should look like:

		vasp_run_inputs_dictionary = {
			'kpoint_scheme': 'Monkhorst',
			'kpoint_subdivisions_list': [4, 4, 4],
			'encut': 800,
			'npar': 1 (optional),
			other incar params
		}
		"""

		self.path = path
		self.reference_structure = reference_structure
		self.hessian = hessian
		self.eigen_pairs_list = hessian.get_sorted_hessian_eigen_pairs_list()
		self.taylor_expansion = copy.deepcopy(taylor_expansion)
		self.vasp_run_inputs_dictionary = copy.deepcopy(vasp_run_inputs_dictionary)
		self.perturbation_magnitudes_dictionary = perturbation_magnitudes_dictionary

		if not reference_completed_vasp_relaxation_run.complete:
			raise Exception("Vasp relaxation for reference structure is not yet completed")

		self.reference_completed_vasp_relaxation_run = reference_completed_vasp_relaxation_run



		self.vasp_static_run_sets_list = None


	def update(self):