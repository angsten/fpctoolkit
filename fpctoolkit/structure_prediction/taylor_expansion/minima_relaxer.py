#from fpctoolkit.structure_prediction.taylor_expansion.minima_relaxer import MinimaRelaxer

import copy
import numpy as np

from fpctoolkit.workflow.vasp_static_run_set import VaspStaticRunSet
from fpctoolkit.util.path import Path
from fpctoolkit.phonon.eigen_structure import EigenStructure
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation



class MinimaRelaxer(object):
	"""
	Takes in a list of eigen_chromosomes that are the minima guesses from the taylor expansion and relaxes these guesses using full vasp relaxations.

	The relaxations are then sortable by energy, and one can see the change in the eigen_chromosomes in going from the guess to the relaxed structure
	"""

	def __init__(self, path, reference_structure, reference_completed_vasp_relaxation_run, hessian, vasp_relaxation_inputs_dictionary, eigen_chromosome_energy_pairs_list):
		"""
		eigen_chromosome_energy_pairs_list should look like [[predicted energy change, guessed eigen_chromosome], [...],...]

		vasp_relaxation_inputs_dictionary should look like:

		vasp_relaxation_inputs_dictionary = 
		{
			'external_relaxation_count': 4,
			'kpoint_schemes_list': ['Gamma'],
			'kpoint_subdivisions_lists': [[1, 1, 1], [1, 1, 2], [2, 2, 4]],
			'submission_script_modification_keys_list': ['100', 'standard', 'standard_gamma'], #optional - will default to whatever queue adapter gives
			'submission_node_count_list': [1, 2],
			'ediff': [0.001, 0.00001, 0.0000001],
			'encut': [200, 400, 600, 800],
			'isif' : [5, 2, 3]
			#any other incar parameters with value as a list
		}
		"""

		Path.make(path)

		self.path = path
		self.reference_structure = reference_structure
		self.reference_completed_vasp_relaxation_run = reference_completed_vasp_relaxation_run
		self.hessian = hessian
		self.eigen_pairs_list = hessian.get_sorted_hessian_eigen_pairs_list()
		self.vasp_relaxation_inputs_dictionary = copy.deepcopy(vasp_relaxation_inputs_dictionary)


		sorted_eigen_chromosome_energy_pairs_list = sorted(eigen_chromosome_energy_pairs_list, key=lambda x: x[0])


		final_pairs_list = []
		energies_list = []
		for eigen_chromosome_energy_pair in sorted_eigen_chromosome_energy_pairs_list:
			if eigen_chromosome_energy_pair[0] in energies_list:
				continue
			else:
				energies_list.append(eigen_chromosome_energy_pair[0])
				final_pairs_list.append(eigen_chromosome_energy_pair)


		print "Final pairs list: "
		print final_pairs_list


		self.predicted_energies_list = [eigen_chromosome_energy_pair[0] for eigen_chromosome_energy_pair in final_pairs_list]
		self.eigen_chromosomes_list = [eigen_chromosome_energy_pair[1] for eigen_chromosome_energy_pair in final_pairs_list]


		self.completed_relaxations_data_list = [] #list of lists with each component like [relaxation, initial chromosome, final chromosome]

		self.vasp_relaxations_list = None

		self.initialize_relaxation_list()



	def initialize_relaxation_list(self):

		self.vasp_relaxations_list = []

		for i, eigen_chromosome in enumerate(self.eigen_chromosomes_list):
			eigen_structure = EigenStructure(reference_structure=self.reference_structure, hessian=self.hessian)
			eigen_structure.set_eigen_chromosome(eigen_chromosome)

			initial_structure = eigen_structure.get_distorted_structure()

			self.vasp_relaxations_list.append(VaspRelaxation(path=self.get_extended_path("rank_" + str(I) + "_" + "_".join(str(x) for x in eigen_chromosome)), initial_structure=initial_structure, input_dictionary=self.vasp_relaxation_inputs_dictionary))


	def update(self):

		self.completed_relaxations_data_list = []

		for i, vasp_relaxation in enumerate(self.vasp_relaxations_list):
			vasp_relaxation.update()

			if vasp_relaxation.complete:
				eigen_structure = EigenStructure(reference_structure=self.reference_structure, hessian=self.hessian, distorted_structure=vasp_relaxation.final_structure)

				self.completed_relaxations_data_list.append([vasp_relaxation, sef.eigen_chromosomes_list[i], eigen_structure.get_list_represenation()])

				print "Structure", str(i)
				print "Predicted Energy Change", str(self.predicted_energies_list[i])
				print "Calculated Energy Change", str(vasp_relaxation.get_final_energy(per_atom=False)-self.reference_completed_vasp_relaxation_run.get_final_energy(per_atom=False))
				print "Original Chromosome"
				print str(self.eigen_chromosomes_list[i])
				print "Final Chromosome"
				print str(eigen_structure.get_list_represenation())


	def get_sorted_relaxation_data_list(self):
		"""
		Returns a list of lists with each component like [relaxation, initial chromosome, final chromosome] sorted by relaxation energy (lowest to highest)
		"""

		pass


	def complete(self):

		for vasp_relaxation in self.vasp_relaxations_list:
			if not vasp_relaxation.complete:
				return False

		return True

	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)