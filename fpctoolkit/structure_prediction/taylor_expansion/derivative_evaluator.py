#from fpctoolkit.structure_prediction.taylor_expansion.derivative_evaluator import DerivativeEvaluator

import copy

from fpctoolkit.workflow.vasp_static_run_set import VaspStaticRunSet
from fpctoolkit.util.path import Path
from fpctoolkit.phonon.eigen_structure import EigenStructure



class DerivativeEvaluator(object):
	"""
	Useful for evaluating the derivatives of taylor expansions with a set of variables that correspond to degrees of freedom of a crystal.

	A central differences approach is used to evaluate all derivative terms.
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
		self.taylor_expansion = taylor_expansion
		self.perturbation_magnitudes_dictionary = perturbation_magnitudes_dictionary

		if not reference_completed_vasp_relaxation_run.complete:
			raise Exception("Vasp relaxation for reference structure is not yet completed")

		self.reference_completed_vasp_relaxation_run = reference_completed_vasp_relaxation_run



		self.vasp_static_run_sets_list = None


		self.update()


	def update(self):

		Path.make(path)

		self.vasp_static_run_sets_list = []

		for expansion_term in self.taylor_expansion.expansion_terms_list:
			self.initialize_vasp_static_run_set(expansion_term)


		for vasp_static_run_set in self.vasp_static_run_sets_list:
			vasp_static_run_set.update()


	def initialize_vasp_static_run_set(self, expansion_term):
		"""
		This sets up a vasp static run set which will calculate the energies necessary to get the derivative for this expansion term.
		"""

		expansion_term_path = self.get_extended_path(str(expansion_term))

		
		perturbed_structures_list = self.get_structures_list(expansion_term)


		self.vasp_static_run_sets_list.append(VaspStaticRunSet(path=expansion_term_path, structures_list=perturbed_structures_list, vasp_run_inputs_dictionary=self.vasp_run_inputs_dictionary, 
			wavecar_path=self.reference_completed_vasp_relaxation_run.get_wavecar_path()))


	def get_structures_list(expansion_term):
		"""
		Get the set of perturbed structures necessary for the given finite differences calculation of this expansion term.
		"""

		derivative_type = expansion_term.get_derivative_type()

		
		np_derivative_arrays_list = []
		np_perturbation_array = expansion_term.get_perturbation_np_derivative_array(self.perturbation_magnitudes_dictionary)

		eigen_structure = EigenStructure(reference_structure=self.reference_structure, hessian=self.hessian)

		if derivative_type == '1':
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [-1.0]))
		elif derivative_type == '2':
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [-1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [1.0]))
		elif derivative_type == '11':
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [-1.0, -1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [-1.0, 1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [1.0, -1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [1.0, 1.0]))
		elif derivative_type == '21':
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [0.0, -1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [0.0, 1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [-1.0, -1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [-1.0, 1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [1.0, -1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [1.0, 1.0]))
		elif derivative_type == '12':
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [-1.0, 0.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [1.0, 0.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [-1.0, -1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [1.0, -1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [-1.0, 1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [1.0, 1.0]))
		elif derivative_type == '4':
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [-1.0]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [-0.5]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [0.5]))
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, [1.0]))			
		else:
			raise Exception("This derivative type is not currently supported", derivative_type)

		return [self.get_distorted_structure_from_eigen_chromosome(np_derivative_array) for np_derivative_array in np_derivative_arrays_list]


	def get_coefficients_dictionary(self):


		coefficients_dictionary = {}

		coefficients_dictionary['1'] =  {'factors':[0.0, 1.0, -1.0], 'perturbations_list': [[1.0], [-1.0]]}
		coefficients_dictionary['2'] =  {'factors':[-2.0, 1.0, 1.0], 'perturbations_list': [[1.0], [-1.0]]}
		coefficients_dictionary['11'] = {'factors':[0.0, 1.0, -1.0, -1.0, 1.0], 'perturbations_list': [[-1.0, -1.0], [-1.0, 1.0], [1.0, -1.0], [1.0, 1.0]]}
		coefficients_dictionary['21'] = {'factors':[0.0 -2.0, 2.0, -1.0, 1.0, -1.0, 1.0], 'perturbations_list': [[0.0, -1.0], [0.0, 1.0], [-1.0, -1.0], [-1.0, 1.0], [1.0, -1.0], [1.0, 1.0]]}
		coefficients_dictionary['21'] = {'factors':[0.0 -2.0, 2.0, -1.0, 1.0, -1.0, 1.0], 'perturbations_list': [[-1.0, 0.0], [1.0, 0.0], [-1.0, -1.0], [1.0, -1.0], [-1.0, 1.0], [1.0, 1.0]]}
		coefficients_dictionary['1'] =  {'factors':[1.0, -1.0], 'perturbations_list': [[1.0], [-1.0]]}
		coefficients_dictionary['1'] =  {'factors':[1.0, -1.0], 'perturbations_list': [[1.0], [-1.0]]}
		coefficients_dictionary['1'] =  {'factors':[1.0, -1.0], 'perturbations_list': [[1.0], [-1.0]]}



	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)



	def multiply_chromosome_components_sequentially_by(self, input_eigen_chromosome, scalars_list):
		"""
		Takes the first non-zero elements of eigen_chromosome and multiplies each by the corresponding scalars list components.
		"""

		eigen_chromosome = copy.deepcopy(input_eigen_chromosome)

		scalar_index = 0
		for i in range(len(eigen_chromosome)):
			if eigen_chromosome[i] != 0:
				eigen_chromosome[i] *= scalars_list[scalar_index]
				scalar_index += 1

		return eigen_chromosome



	def get_distorted_structure_from_eigen_chromosome(eigen_chromosome):

		eigen_structure = EigenStructure(reference_structure=self.reference_structure, hessian=self.hessian)
		eigen_structure.set_eigen_chromosome(eigen_chromosome)
		return eigen_structure.get_distorted_structure()