#from fpctoolkit.structure_prediction.taylor_expansion.derivative_evaluator import DerivativeEvaluator

import copy
import numpy as np

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
		self.eigen_pairs_list = hessian.get_sorted_hessian_eigen_pairs_list()
		self.taylor_expansion = copy.deepcopy(taylor_expansion)
		self.vasp_run_inputs_dictionary = copy.deepcopy(vasp_run_inputs_dictionary)
		self.perturbation_magnitudes_dictionary = perturbation_magnitudes_dictionary

		if not reference_completed_vasp_relaxation_run.complete:
			raise Exception("Vasp relaxation for reference structure is not yet completed")

		self.reference_completed_vasp_relaxation_run = reference_completed_vasp_relaxation_run



		self.vasp_static_run_sets_list = None


	def update(self):

		Path.make(self.path)

		self.vasp_static_run_sets_list = []

		#u^2 and u^4 coefficients
		for displacement_variable in self.taylor_expansion.get_active_variables_list(type_string='displacement'):
			print "Running static for " + str(displacement_variable)

			vasp_static_run_set = self.get_pure_displacement_vasp_static_run_set(displacement_variable.index)

			if vasp_static_run_set.complete:
				displacement_magnitudes_list = self.get_pure_eigen_chromosome_components_from_distorted_structures_list(vasp_static_run_set.get_final_structures_list())
				energies_list = vasp_static_run_set.get_final_energies_list()

				for i in range(len(energies_list)-1, -1, -1):
					print -1.0*displacement_magnitudes_list[i], energies_list[i]

				for i in range(len(energies_list)):
					print displacement_magnitudes_list[i], energies_list[i]

			else:
				vasp_static_run_set.update()


		#e^2 terms
		for strain_variable in self.taylor_expansion.get_active_variables_list(type_string='strain'):
			print "Running static for " + str(strain_variable)

			vasp_static_run_set = self.get_pure_strain_vasp_static_run_set(strain_variable.index)

			if vasp_static_run_set.complete:
				strain_magnitudes_list = self.get_pure_eigen_chromosome_components_from_distorted_structures_list(vasp_static_run_set.get_final_structures_list())
				energies_list = vasp_static_run_set.get_final_energies_list()

				for i in range(len(energies_list)):
					print strain_magnitudes_list[i], energies_list[i]
			else:
				vasp_static_run_set.update()


		#e*u^2 terms
		for strain_variable in self.taylor_expansion.get_active_variables_list(type_string='strain'):
			for displacement_variable in self.taylor_expansion.get_active_variables_list(type_string='displacement'):
				print "Running static for " + str(strain_variable) + str(displacement_variable)

				for i in range(-5, 6):
					strain = i*self.perturbation_magnitudes_dictionary['strain']

					path = self.get_extended_path(str(strain_variable) + str(displacement_variable) + "_" + str(strain).replace('.', 'o').replace('-', 'n'))
					

					eigen_chromosome = [0.0]*(3*self.reference_structure.site_count)
					eigen_chromosome[strain_variable.index] = strain

					structure = self.get_distorted_structure_from_eigen_chromosome(eigen_chromosome)

					print str(strain), str(self.get_displacement_second_derivative(path, structure, displacement_variable.index))



		# for expansion_term in self.taylor_expansion.expansion_terms_list:

		# 	vasp_static_run_set = self.get_vasp_static_run_set(expansion_term)

		# 	if vasp_static_run_set.complete:
		# 		self.set_taylor_coefficient(vasp_static_run_set, expansion_term)
		# 		vasp_static_run_set.delete_wavecars_of_completed_runs()
		# 	else:
		# 		vasp_static_run_set.update()


	def get_pure_displacement_vasp_static_run_set(self, displacement_variable_index):

		displacement_run_set_path = self.get_extended_path('u_' + str(displacement_variable_index+1))

		perturbed_structures_list = self.get_pure_displacement_structures_list(displacement_variable_index)

		return VaspStaticRunSet(path=displacement_run_set_path, structures_list=perturbed_structures_list, vasp_run_inputs_dictionary=self.vasp_run_inputs_dictionary, 
			wavecar_path=self.reference_completed_vasp_relaxation_run.get_wavecar_path())

	def get_pure_strain_vasp_static_run_set(self, strain_variable_index):

		strain_run_set_path = self.get_extended_path('e_' + str(strain_variable_index+1))

		perturbed_structures_list = self.get_pure_strain_structures_list(strain_variable_index)

		return VaspStaticRunSet(path=strain_run_set_path, structures_list=perturbed_structures_list, vasp_run_inputs_dictionary=self.vasp_run_inputs_dictionary, 
			wavecar_path=self.reference_completed_vasp_relaxation_run.get_wavecar_path())		

	def get_pure_displacement_structures_list(self, displacement_variable_index):
		"""
		Get the set of perturbed structures necessary for the given finite differences calculation of this expansion term.
		"""

		displacement_step_size = self.perturbation_magnitudes_dictionary['displacement'] #in Angstroms

		eigen_chromosomes_list = []

		for i in range(1, 9):
			eigen_chromosome = [0.0]*(3*self.reference_structure.site_count)
			eigen_chromosome[displacement_variable_index + 6] = i*displacement_step_size

			eigen_chromosomes_list.append(eigen_chromosome)

		return [self.get_distorted_structure_from_eigen_chromosome(eigen_chromosome) for eigen_chromosome in eigen_chromosomes_list]


	def get_pure_strain_structures_list(self, strain_variable_index):
		"""
		Get the set of perturbed structures necessary for the given finite differences calculation of this expansion term.
		"""

		strain_step_size = self.perturbation_magnitudes_dictionary['strain'] #in Angstroms

		eigen_chromosomes_list = []

		for i in range(-8, 9):
			eigen_chromosome = [0.0]*(3*self.reference_structure.site_count)
			eigen_chromosome[strain_variable_index] = i*strain_step_size

			eigen_chromosomes_list.append(eigen_chromosome)

		return [self.get_distorted_structure_from_eigen_chromosome(eigen_chromosome) for eigen_chromosome in eigen_chromosomes_list]


	def get_distorted_structure_from_eigen_chromosome(self, eigen_chromosome):

		eigen_structure = EigenStructure(reference_structure=self.reference_structure, hessian=self.hessian)
		eigen_structure.set_eigen_chromosome(eigen_chromosome)
		return eigen_structure.get_distorted_structure()




	def get_pure_eigen_chromosome_components_from_distorted_structures_list(self, distorted_structures_list):

		eigen_chromosome_pure_components_list = []

		for distorted_structure in distorted_structures_list:
			eigen_structure = EigenStructure(reference_structure=self.reference_structure, hessian=self.hessian, distorted_structure=distorted_structure)

			eigen_chromosome = eigen_structure.get_list_representation()

			if np.count_nonzero(eigen_chromosome) > 1:
				raise Exception("There should only be one non-zero component")

			eigen_chromosome_pure_components_list.append(sum(eigen_chromosome))

		return eigen_chromosome_pure_components_list



	def get_displacement_second_derivative(self, path, structure, displacement_variable_index):
		"""
		Determines the second derivative of the energy w.r.t. the given displacement variable for structure.

		Returns None if not done yet
		"""

		displacement_factor = 0.01 #hardcoded!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

		central_difference_coefficients_dictionary = {}
		central_difference_coefficients_dictionary['1'] =  {'factors':[0.0, -1.0, 8.0, -8.0, 1.0], 'perturbations_list': [[2.0], [1.0], [-1.0], [-2.0]]}


		perturbed_structures_list = []

		for perturbation_magnitude in central_difference_coefficients_dictionary['1']['perturbations_list']:
			eigen_structure = EigenStructure(reference_structure=self.reference_structure, hessian=self.hessian, distorted_structure=structure)

			eigen_structure[displacement_variable_index+6] = perturbation_magnitude[0]*displacement_factor

			perturbed_structures_list.append(eigen_structure.get_distorted_structure())

		perturbed_structures_list

		vasp_static_run_set = VaspStaticRunSet(path=path, structures_list=perturbed_structures_list, vasp_run_inputs_dictionary=self.vasp_run_inputs_dictionary, 
			wavecar_path=self.reference_completed_vasp_relaxation_run.get_wavecar_path())

		if vasp_static_run_set.complete:

			term_factors_list = central_difference_coefficients_dictionary['1']['factors']

			force_sums_list = [0.0] + self.get_force_sums(vasp_static_run_set, displacement_variable_index)

			numerator = sum(map(lambda x, y: -x*y, term_factors_list, force_sums_list))
			denominator = 12.0*displacement_factor

			return numerator/denominator

		else:
			vasp_static_run_set.update()

			return None






	def get_vasp_static_run_set(self, expansion_term):
		"""
		This sets up a vasp static run set which will calculate the energies necessary to get the derivative for this expansion term.
		"""

		expansion_term_path = self.get_extended_path(str("_".join(str(x) for x in expansion_term.derivative_array)))

		
		perturbed_structures_list = self.get_structures_list(expansion_term)

		return VaspStaticRunSet(path=expansion_term_path, structures_list=perturbed_structures_list, vasp_run_inputs_dictionary=self.vasp_run_inputs_dictionary, 
			wavecar_path=self.reference_completed_vasp_relaxation_run.get_wavecar_path())


	def get_structures_list(self, expansion_term):
		"""
		Get the set of perturbed structures necessary for the given finite differences calculation of this expansion term.
		"""

		modified_expansion_term = copy.deepcopy(expansion_term)

		if not modified_expansion_term.is_pure_type('strain'):
			modified_expansion_term.lower_first_displacement_order()

		derivative_type = modified_expansion_term.get_derivative_type()

		
		np_derivative_arrays_list = []

		#if term's derivative array is [2, 4, 0, 0, 0, 0, 1], np_perturbations_array will be [strain_mag, strain_mag, 0, 0, 0, 0, displacement_mag]
		np_perturbation_array = modified_expansion_term.get_perturbation_np_derivative_array(self.perturbation_magnitudes_dictionary)

		term_coefficients_dictionary = self.get_central_difference_coefficients_dictionary()[derivative_type]


		for perturbation_factors_list in term_coefficients_dictionary['perturbations_list']:
			np_derivative_arrays_list.append(self.multiply_chromosome_components_sequentially_by(np_perturbation_array, perturbation_factors_list))

		return [self.get_distorted_structure_from_eigen_chromosome(np_derivative_array) for np_derivative_array in np_derivative_arrays_list]



	def set_taylor_coefficient(self, vasp_static_run_set, expansion_term):
		"""
		Sets the derivative_coefficient_value attribute of expansion_term based on the energies in vasp_static_run_set.
		"""

		print "\nSetting taylor coefficient for", str(expansion_term)

		modified_expansion_term = copy.deepcopy(expansion_term)


		if modified_expansion_term.is_pure_type('strain'):
			# print "All strain - getting energies"

			term_coefficients_dictionary = self.get_central_difference_coefficients_dictionary()[modified_expansion_term.get_derivative_type()]
			term_factors_list = term_coefficients_dictionary['factors']

			energies_list = [self.reference_completed_vasp_relaxation_run.get_final_energy()] + vasp_static_run_set.get_final_energies_list(per_atom=False)

			# print "Energies: ", str(energies_list)

			numerator = sum(map(lambda x, y: x*y, term_factors_list, energies_list))

			denominator = self.get_denominator(modified_expansion_term)
		else:
			modified_expansion_term.lower_first_displacement_order()

			term_coefficients_dictionary = self.get_central_difference_coefficients_dictionary()[modified_expansion_term.get_derivative_type()]
			term_factors_list = term_coefficients_dictionary['factors']

			#assume no forces on initial structures
			force_sums_list = [0.0] + self.get_force_sums(vasp_static_run_set, expansion_term.get_first_displacement_index())

			numerator = sum(map(lambda x, y: -x*y, term_factors_list, force_sums_list))

			denominator = self.get_denominator(modified_expansion_term)

		print "Numerator: ", str(numerator)
		print "Denominator:", str(denominator)


		expansion_term.derivative_coefficient = numerator/denominator


	def get_force_sums(self, vasp_static_run_set, first_displacement_index):
		"""
		Returns a list of weighted force sums for each static calculation. Basically, this takes -1.0*eigenvector of the first displacement expansion term and dots
		it with the force set of the run. This gives dE/dA
		"""

		first_displacement_index = expansion_term.get_first_displacement_index()

		basis_vector = np.array(self.eigen_pairs_list[first_displacement_index].eigenvector)

		forces_sums_list = []

		forces_lists = vasp_static_run_set.get_forces_lists()


		return [np.dot(np.array(forces_list), basis_vector) for forces_list in forces_lists]






	def get_term_coefficients(self, expansion_term):

		derivative_type = expansion_term.get_derivative_type()

		term_coefficients_dictionary = self.get_central_difference_coefficients_dictionary()[derivative_type]



	def get_denominator(self, expansion_term):

		derivative_type = expansion_term.get_derivative_type()

		#if term's derivative array is [2, 4, 0, 0, 0, 0, 1], np_perturbations_array will be [strain_mag, strain_mag, 0, 0, 0, 0, displacement_mag]
		np_perturbation_array = expansion_term.get_perturbation_np_derivative_array(self.perturbation_magnitudes_dictionary)

		non_zero_list = [pert for pert in np_perturbation_array if pert != 0.0]

		if derivative_type == '1':
			#return 2.0*non_zero_list[0]
			return 12.0*non_zero_list[0]
		elif derivative_type == '2':
			#return non_zero_list[0]**2.0
			return 12.0*non_zero_list[0]**2.0
		elif derivative_type == '11':
			#return 4.0*non_zero_list[0]*non_zero_list[1]
			return 600.0*non_zero_list[0]*non_zero_list[1]
		# elif derivative_type == '21':
		# 	return 2.0*(non_zero_list[0]**2.0)*non_zero_list[1]
		# elif derivative_type == '12':
		# 	return 2.0*non_zero_list[0]*(non_zero_list[1]**2.0)
		# elif derivative_type == '111':
		# 	return 8.0*non_zero_list[0]*non_zero_list[1]*non_zero_list[2]
		elif derivative_type == '3':
			return 112.0*non_zero_list[0]**3.0
			#return 8.0*non_zero_list[0]**3.0
		# elif derivative_type == '4':
		# 	return (1.0/16.0)*non_zero_list[0]**4.0
		else:
			raise Exception("Derivative type not supported: ", derivative_type)



	def get_central_difference_coefficients_dictionary(self):
		"""
		This returns a dictionary which forms the structure of central difference calculations. The factors key points to a list of coefficients that go
		before the funciton outputs (the first is for the unperturbed structure), the perturbations_list tracks what the non-zero perturbations should look like.
		"""

		central_difference_coefficients_dictionary = {}

		#central_difference_coefficients_dictionary['1'] =  {'factors':[0.0, 1.0, -1.0], 'perturbations_list': [[1.0], [-1.0]]}
		central_difference_coefficients_dictionary['1'] =  {'factors':[0.0, -1.0, 8.0, -8.0, 1.0], 'perturbations_list': [[2.0], [1.0], [-1.0], [-2.0]]}

		central_difference_coefficients_dictionary['2'] =  {'factors':[-30.0, -1.0, 16.0, 16.0, -1.0], 'perturbations_list': [[2.0], [1.0], [-1.0], [-2.0]]}

		#central_difference_coefficients_dictionary['11'] = {'factors':[0.0, 1.0, -1.0, -1.0, 1.0], 'perturbations_list': [[-1.0, -1.0], [-1.0, 1.0], [1.0, -1.0], [1.0, 1.0]]}
		central_difference_coefficients_dictionary['11'] = {'factors':[0.0, -63.0, -63.0, -63.0, -63.0, 63.0, 63.0, 63.0, 63.0, 44.0, 44.0, -44.0, -44.0, 74.0, 74.0, -74.0, -74.0, ], 'perturbations_list': [[1.0, -2.0], [2.0, -1.0], [-2.0, 1.0], [-1.0, 2.0], [-1.0, -2.0], [-2.0, -1.0], [1.0, 2.0], [2.0, 1.0], [2.0, -2.0], [-2.0, 2.0], [-2.0, -2.0], [2.0, 2.0], [-1.0, -1.0], [1.0, 1.0], [1.0, -1.0], [-1.0, 1.0]]}


		#central_difference_coefficients_dictionary['21'] = {'factors':[0.0, -2.0, 2.0, -1.0, 1.0, -1.0, 1.0], 'perturbations_list': [[0.0, -1.0], [0.0, 1.0], [-1.0, -1.0], [-1.0, 1.0], [1.0, -1.0], [1.0, 1.0]]}
		#central_difference_coefficients_dictionary['12'] = {'factors':[0.0, -2.0, 2.0, -1.0, 1.0, -1.0, 1.0], 'perturbations_list': [[-1.0, 0.0], [1.0, 0.0], [-1.0, -1.0], [1.0, -1.0], [-1.0, 1.0], [1.0, 1.0]]}
		#central_difference_coefficients_dictionary['111'] = {'factors':[0.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0, 1.0], 'perturbations_list': [[-1.0, -1.0, -1.0], [-1.0, -1.0, 1.0], [-1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]]}		
		#central_difference_coefficients_dictionary['3'] =  {'factors':[0.0, -1.0, 8.0, -13.0, 13.0, -8.0, 1.0], 'perturbations_list': [[3.0], [2.0], [1.0], [-1.0], [-2.0], [-3.0]]}
				
		central_difference_coefficients_dictionary['3'] =  {'factors':[0.0, 3.0, -4.0, -70.0, 140.0, -140.0, 70.0, 4.0, -3.0], 'perturbations_list': [[-4.0], [-3.0], [-2.0], [-1.0], [1.0], [2.0], [3.0], [4.0]]}

		#central_difference_coefficients_dictionary['4'] =  {'factors':[6.0, 1.0, -4.0, -4.0, 1.0], 'perturbations_list': [[-1.0], [-0.5], [0.5], [1.0]]}

		return central_difference_coefficients_dictionary


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








	def get_mock_energy(self, structure):

		eigen_structure = EigenStructure(reference_structure=self.reference_structure, hessian=self.hessian, distorted_structure = structure)

		chromosome = eigen_structure.get_list_representation()


		e_1 = chromosome[0]
		e_2 = chromosome[1]
		e_3 = chromosome[2]
		e_4 = chromosome[3]
		e_5 = chromosome[4]
		e_6 = chromosome[5]

		u_1 = chromosome[6]
		u_2 = chromosome[7]

		return 0.234*e_3**2 + -0.52113*e_4**2 + 0.0*e_5**2 + 400.23*e_3*e_4 + 0.00034*e_4*e_5 + 3.2*u_1**2 + 0.001*u_1*u_2 + 0.0*u_2**2 + 7034.0234944959*u_1*u_2*e_4 + 93.0*u_2**2*e_5 + 1.8*u_1**4 + -9345.02*e_3*u_1**2 + 0.445*u_2**4
