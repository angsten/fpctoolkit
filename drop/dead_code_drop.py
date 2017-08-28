#from fpctoolkit.workflow.epitaxial_relaxer import EpitaxialRelaxer

import numpy as np
import copy
from collections import OrderedDict

from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.workflow.vasp_run_set import VaspRunSet
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.structure.structure import Structure
from fpctoolkit.io.file import File
import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.workflow.vasp_polarization_run_set import VaspPolarizationRunSet

class EpitaxialRelaxer(object):
	"""
	Calculates the minimum energy structures across a series of (100) misfit strains.
	"""

	def __init__(self, path, initial_structures_list, reference_structure, vasp_relaxation_inputs_dictionary, reference_lattice_constant, misfit_strains_list, supercell_dimensions_list, calculate_polarizations=False):
		"""
		path should be the main path of the calculation set

		initial_structures_list should be the set of structures that are relaxed at each misfit strain

		reference structure can have any lattice but its atom positions must be in direct coords as the positions to compare polarizations to (choose a centrosymmetric structure if possible)

		vasp_relaxation_inputs_dictionary should look something like:
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

		reference_lattice_constant should be the lattice constant a0 which, when multiplied by the list of misfit strains, generates the new in-plane lattice constant at those strains.

		For each lattice constant and each structure, a relaxation is performed. Then, the lowest energy structures at each misfit strain can be determined, and a convex hull results.
		"""

		for structure in initial_structures_list:
			Structure.validate(structure)

		basic_validators.validate_real_number(reference_lattice_constant)

		for misfit_strain in misfit_strains_list:
			basic_validators.validate_real_number(misfit_strain)


		self.path = path
		self.initial_structures_list = initial_structures_list
		self.reference_structure = reference_structure
		self.vasp_relaxation_inputs_dictionary = vasp_relaxation_inputs_dictionary
		self.reference_lattice_constant = reference_lattice_constant
		self.misfit_strains_list = misfit_strains_list
		self.supercell_dimensions_list = supercell_dimensions_list
		self.calculate_polarizations = calculate_polarizations

		Path.make(path)

		self.initialize_vasp_relaxations()


	def initialize_vasp_relaxations(self):
		"""
		"""

		for misfit_strain in self.misfit_strains_list:
			lattice_constant = self.reference_lattice_constant*(1.0+misfit_strain)

			misfit_path = self.get_extended_path(str(misfit_strain).replace('-', 'n'))

			Path.make(misfit_path)

			for i, initial_structure in enumerate(self.initial_structures_list):

				#if self.structure_is_duplicate(initial_structure, misfit_path): #####################FIX THIS AND PUT BACK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
				#	print "Duplicate structure found - skipping"
				#	continue

				structure = copy.deepcopy(initial_structure)

				if abs(structure.lattice[0][1]) > 0.0 or abs(structure.lattice[0][2]) > 0.0 or abs(structure.lattice[1][0]) > 0.0 or abs(structure.lattice[1][2]) > 0.0:
					raise Exception("Current lattice is incompatible with (100) epitaxy: ", str(structure.lattice))

				structure.lattice[0][0] = lattice_constant*self.supercell_dimensions_list[0]
				structure.lattice[1][1] = lattice_constant*self.supercell_dimensions_list[1]

				#break symmetry
				structure.randomly_displace_sites(max_displacement_magnitude=0.01)


				relax_path = Path.join(misfit_path, 'structure_' + str(i))

				if not Path.exists(relax_path):
					print "Initializing epitaxial relaxation at " + relax_path

				relaxation = VaspRelaxation(path=relax_path, initial_structure=structure, input_dictionary=self.vasp_relaxation_inputs_dictionary)

				initial_structure.to_poscar_file_path(Path.join(relax_path, 'original_initial_structure'))


	def structure_is_duplicate(self, structure, misfit_path):
		"""
		Returns true if this has been the initial structure for any previous relaxation
		"""

		for i in range(10000):
			relax_path = Path.join(misfit_path, 'structure_' + str(i))

			if not Path.exists(relax_path):
				return False
			else:
				comparison_structure = Structure(file_path=Path.join(relax_path, 'original_initial_structure'))

				if structure.is_equivalent_to_structure(comparison_structure):
					print "FOUND DUPLICATE in epitaxial_relaxer.py"
					return True


	def update(self):

		for misfit_strain in self.misfit_strains_list:

			misfit_path = self.get_extended_path(str(misfit_strain).replace('-', 'n'))

			for i in range(10000):
				relax_path = Path.join(misfit_path, 'structure_' + str(i))

				if not Path.exists(relax_path):
					break

				
				relaxation = VaspRelaxation(path=relax_path)

				relaxation.update()

				print "Updating Epitaxial Relax run at " + relax_path + "  Status is " + relaxation.get_status_string()

				if self.calculate_polarizations and relaxation.complete:
					self.update_polarization_run(relaxation)

	@property
	def complete(self):
		for misfit_strain in self.misfit_strains_list:
			misfit_path = self.get_extended_path(str(misfit_strain).replace('-', 'n'))

			for i in range(10000):
				relax_path = Path.join(misfit_path, 'structure_' + str(i))

				if not Path.exists(relax_path):
					return True
				else:
					relaxation = VaspRelaxation(path=relax_path)

					if not relaxation.complete:
						return False

	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)

	def update_polarization_run(self, relaxation):

		if not relaxation.complete:
			return

		path = relaxation.path
		reference_structure = self.reference_structure
		distorted_structure = relaxation.final_structure
		reference_structure.lattice = copy.deepcopy(distorted_structure.lattice)
		vasp_run_inputs_dictionary = {
			'kpoint_scheme': relaxation.kpoint_schemes[100],
			'kpoint_subdivisions_list': relaxation.kpoint_subdivisions_lists[100],
			'encut': relaxation.incar_modifier_lists_dictionary['encut'][100],
			'lreal': False,
			'ediff': 1e-8,
			'isym': 0
		}


		polarization_run = VaspPolarizationRunSet(path, reference_structure, distorted_structure, vasp_run_inputs_dictionary)

		polarization_run.update()

		return polarization_run.get_change_in_polarization()

	def get_data_dictionaries_list(self, get_polarization=False):
		"""
		Starts at most negative misfit runs and goes to larger misfits finding the minimum energy data set. To encourage continuity, if two or more relaxations are within a small energy threshold of each other, the 
		structure that is closest to the last chosen structure is chosen.

		The output of this function looks like [[-0.02, energy_1, [polarization_vector_1]], [-0.015, energy_2, [polarization_vector_2]], ...]
		"""

		output_data_dictionaries = []
		spg_symprecs = [0.1, 0.05, 0.04, 0.03, 0.02, 0.01, 0.001]

		for misfit_strain in self.misfit_strains_list:
			# print str(misfit_strain)
			data_dictionary = OrderedDict()
			data_dictionary['misfit_strain'] = misfit_strain

			misfit_path = self.get_extended_path(str(misfit_strain).replace('-', 'n'))

			minimum_energy = 10000000000
			minimum_energy_relaxation = None
			for i in range(10000):
				relax_path = Path.join(misfit_path, 'structure_' + str(i))

				if not Path.exists(relax_path):
					break

				relaxation = VaspRelaxation(path=relax_path)

				if not relaxation.complete:
					continue

				energy = relaxation.get_final_energy(per_atom=False)
				# print 'structure_' + str(i), energy
				
				if energy < minimum_energy:
					minimum_energy = energy
					minimum_energy_relaxation = relaxation

			# print 
			# print "minimum E " + str(minimum_energy)
			# print 
			
			if minimum_energy_relaxation == None:
				data_dictionary['structure'] = None
				data_dictionary['energy'] = None
				data_dictionary['polarization_vector'] = None

				for symprec in spg_symprecs:
					data_dictionary['spg_' + str(symprec)] = None

				data_dictionary['path'] = None
			else:				

				structure = copy.deepcopy(minimum_energy_relaxation.final_structure)

				if get_polarization:
					polarization_vector = self.update_polarization_run(minimum_energy_relaxation)
				else:
					polarization_vector = None

				data_dictionary['structure'] = structure
				data_dictionary['energy'] = minimum_energy
				data_dictionary['polarization_vector'] = polarization_vector

				for symprec in spg_symprecs:
					data_dictionary['spg_' + str(symprec)] = structure.get_spacegroup_string(symprec)

				data_dictionary['path'] = Path.join(minimum_energy_relaxation.path, 'static')

			output_data_dictionaries.append(data_dictionary)

		return output_data_dictionaries

#from fpctoolkit.phonon.phonon_structure import PhononStructure

import numpy as np
import copy
from collections import OrderedDict
import math
import cmath

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.structure_manipulator import StructureManipulator
from fpctoolkit.phonon.normal_coordinate import NormalCoordinate
from fpctoolkit.util.math.vector import Vector
from fpctoolkit.phonon.phonon_super_displacement_vector import PhononSuperDisplacementVector

class PhononStructure(object):
	"""
	Represents a structure whose distortions are characterized by a set of 'complex normal coordinates', Q_q,j (see around page 298 of Born and Huang and pages preceding).
	"""

	def __init__(self, primitive_cell_structure, phonon_band_structure, supercell_dimensions_list, normal_coordinate_instances_list=None):
		"""
		primitive_cell_structure should be the primitive cell Structure class instance that was used to generate the phonon band structure.

		phonon_band_structure should be a PhononBandStructure instance with, at minimim, normal modes for the necessary wave vectors, loosely (38.10, pg 295 Born and Huang)
		-->For example, if a 2x1x1 supercell is expected, the following q points must be provided: (+1/2, 0, 0), (0, 0, 0)

		supercell_dimensions

		if normal_coordinate_instances_list, this list is used to set the normal coordinates, else, the normal coordinates are initialized to zero.
		"""

		Structure.validate(primitive_cell_structure)

		self.primitive_cell_structure = primitive_cell_structure
		self.phonon_band_structure = phonon_band_structure
		self.supercell_dimensions_list = supercell_dimensions_list


		self.reference_supercell_structure = StructureManipulator.get_supercell(primitive_cell_structure, supercell_dimensions_list)



		self.validate_necessary_wave_vectors_exist()


		#FIX::self.number_of_normal_coordinates = 2*self.primitive_cell_structure.site_count*3*supercell_dimensions_list[0]*supercell_dimensions_list[1]*supercell_dimensions_list[2]


		if normal_coordinate_instances_list != None:
			# if len(normal_coordinate_instances_list) != self.number_of_normal_coordinates:
			# 	raise Exception("The number of given normal coordinates is not equal to the number needed to describe the structural distortions. Normal coordinates list given is", normal_coordinate_instances_list)
			# else:
			self.normal_coordinates_list = copy.deepcopy(normal_coordinate_instances_list)
		else:
			self.initialize_normal_coordinates_list()

	def __str__(self):
		return "[\n" + "\n".join(str(normal_coordinate) for normal_coordinate in self.normal_coordinates_list) + "\n]"


	def initialize_normal_coordinates_list(self):

		self.normal_coordinates_list = []

		for normal_mode in self.phonon_band_structure.get_list_of_normal_modes():
			for lambda_index in [1, 2]:
				displacement_vector = PhononSuperDisplacementVector(normal_mode_instance=normal_mode, lambda_index=lambda_index, 
					reference_supercell=self.reference_supercell_structure, supercell_dimensions_list=self.supercell_dimensions_list)

				normal_coordinate = NormalCoordinate(normal_mode_instance=normal_mode, lambda_index=lambda_index, coefficient=0.0, 
					phonon_super_displacement_vector_instance=displacement_vector)

				self.normal_coordinates_list.append(normal_coordinate)


	def validate_necessary_wave_vectors_exist(self):
		"""
		Validates that (at minimum) all necessary wavevectors for the given supercell_dimensions are in phonon_band_structure.
		"""

		necessary_q_vectors_list = self.get_necessary_wave_vectors_listt()

		for q_vector in necessary_q_vectors_list:
			if q_vector not in self.phonon_band_structure:
				raise Exception("Phonon band structure does not contain all necessary q_vectors. Missing ", q_vector)





	def get_necessary_wave_vectors_listt(self):
		"""
		Using equation 38.10 from B+H, determine all necessary wave vectors for the given supercell dimensions (resulting q's are in
		fractional coordinates)
		"""

		return PhononStructure.get_necessary_wave_vectors_list(self.supercell_dimensions_list)



	def get_distorted_supercell_structure(self):
		"""
		Returns a supercell of self.primitive_cell_structure with dimensions self.supercell_dimensions_list with the phonon eigen_displacements applied, as
		controlled by self.normal_coordinates_list
		"""

		distorted_structure = copy.deepcopy(self.reference_supercell_structure)

		distorted_structure.convert_sites_to_direct_coordinates()

		for site_count, site in enumerate(distorted_structure.sites):
			#print site_count, site
			#index to cite number in the primitive cell - can range from 0 to Nat-1, where there are Nat in the primitive cell
			atom_index = int(site_count/(self.supercell_dimensions_list[0]*self.supercell_dimensions_list[1]*self.supercell_dimensions_list[2]))

			#print 'atom_index is ', atom_index

			#this marks the cell the site is in - for instance, 1, 1, 1 in a 2x2x2 supercell means I'm in the center of the supercell
			site_supercell_position = [site['position'][i]*self.supercell_dimensions_list[i] for i in range(3)] 

			cartesian_displacement = [0.0, 0.0, 0.0]


			# # print site_supercell_position
			# if site_supercell_position == [0.5, 0.5, 0.5]:###################remove
			# 	b = True
			# else:
			# 	b = False

			for normal_coordinate in self.normal_coordinates_list:

				for i in range(2): #once for both -q and +q

					if i == 1 and normal_coordinate.normal_mode.q_point_fractional_coordinates == (0.0, 0.0, 0.0):
						continue

					if i == 0:
						q_vector = normal_coordinate.normal_mode.q_point_fractional_coordinates
						eigen_displacements_vector = normal_coordinate.normal_mode.eigen_displacements_list[3*atom_index:3*atom_index+3]
						normal_coordinate_complex_coefficient = normal_coordinate.complex_coefficient
					else:
						q_vector = [-component for component in normal_coordinate.normal_mode.q_point_fractional_coordinates]
						eigen_displacements_vector = np.conj(normal_coordinate.normal_mode.eigen_displacements_list[3*atom_index:3*atom_index+3])
						normal_coordinate_complex_coefficient = np.conj(normal_coordinate.complex_coefficient)

					displacement_vector = normal_coordinate_complex_coefficient*eigen_displacements_vector*cmath.exp(2.0*math.pi*(1.0j)*np.dot(q_vector, site_supercell_position))

					if b:
						print displacement_vector

					for i in range(3):
						cartesian_displacement[i] += displacement_vector[i]

			for cartesian_component in cartesian_displacement:
				if abs(cartesian_component.imag) > 1e-6:
					raise Exception("Distortion displacement vector has imaginary component. Vector in Cartesian coordinates is", cartesian_displacement)


			real_cartesian_displacement_vector = [component.real for component in cartesian_displacement]

			direct_coordinates_displacement = Vector.get_in_direct_coordinates(real_cartesian_displacement_vector, distorted_structure.lattice).to_list()

			#print "Displacement: ", direct_coordinates_displacement

			site.displace(direct_coordinates_displacement)
		
		return distorted_structure


	def set_translational_coordinates_to_zero(self):
		"""
		Sets all components of self.Q_coordinates_list that correspond to a translational normal mode that doesn't affect the structure's energy.
		"""

		pass

	@staticmethod
	def get_normal_coordinates_list_from_supercell_structure(self, supercell_structure):
		"""
		Returns a list of complex normal coordinates (Q) based on the current phonon band structure and the displacements in supercell_structure.
		Supercell_structure must be consistent in dimensions with self.supercell_dimensions.
		"""

		pass


	@staticmethod
	def get_necessary_wave_vectors_list(supercell_dimensions_list):
		"""
		Using equation 38.10 from B+H, determine all necessary wave vectors for the given supercell dimensions (resulting q's are in
		fractional coordinates). In this version, don't every use -q and q - just positive q's are sufficient.

		For example, for a 2x1x1 supercell, returned q points will be [(0.5, 0, 0), (0, 0, 0)]
		"""

		necessary_q_vectors_list = []
		L_x = supercell_dimensions_list[0]
		L_y = supercell_dimensions_list[1]
		L_z = supercell_dimensions_list[2]

		for l_x in range(0, L_x):
			for l_y in range(0, L_y):
				for l_z in range(0, L_z):
					q_point_x = float(l_x)/float(L_x)
					q_point_y = float(l_y)/float(L_y)
					q_point_z = float(l_z)/float(L_z)

					q_point = (q_point_x, q_point_y, q_point_z)

					q_point_necessary = True

					for q_component in q_point:
						if (q_component > (0.5)):
							q_point_necessary = False

					if q_point_necessary:
						necessary_q_vectors_list.append(q_point)

		# if len(necessary_q_vectors_list) != L_x*L_y*L_z:
		# 	raise Exception("Number of necessary wave-vectors must equal the number of cells in the supercell.")

		return necessary_q_vectors_list

	def save(self):
		"""Saves class to pickled file at {self.path}/.run_pickle
		"""

		self.log("Saving run")

		#We don't want to waste space with storing full potcars - just store basenames and recreate on loading
		# self.potcar_minimal_form = self.potcar.get_minimal_form()
		# stored_potcar = self.potcar
		# self.potcar = None

		save_path = self.get_save_path()

		# file = open(save_path, 'w')
		# file.write(cPickle.dumps(self.__dict__))
		# file.close()

		# self.potcar = stored_potcar

		self.log("Save successful")

	def load(self, load_path=None):
		# previous_path = self.path
		# previous_verbose = self.verbose

		self.log("Loading run")

		# if not load_path:
		# 	load_path = self.get_save_path()

		# if not Path.exists(load_path):
		# 	self.log("Load file path does not exist: " + load_path, raise_exception=True)

		# file = open(load_path, 'r')
		# data_pickle = file.read()
		# file.close()

		# self.__dict__ = cPickle.loads(data_pickle)
		# self.verbose = previous_verbose #so this can be overridden upon init
		# self.path = previous_path #in case run is moved

		# #restore the full potcar from the basenames that were saved
		# if self.potcar_minimal_form:
		# 	self.potcar = Potcar(minimal_form=self.potcar_minimal_form)
		# 	del self.potcar_minimal_form


	def randomly_displace_site_positions(self, stdev, enforced_minimum_atomic_distance=None, max_displacement_distance=None, mean=0.0, types_list=None):
		"""
		Randomly displace all sites in separate random directions with
		displacement magnitude governed by a normal distribution.
		Note: mean effectively is the shell about which atoms on average sit around there original position.
		!!Parameters are given in angstroms!!
		These will be converted to direct coordinates for sites represented
		in direct coordinates. Modifies self.

		Note: This method is suboptimal for preserving the distributions of displacements in certain cases

		If types_list is specified, only sites with type in types_list will be perturbed

		returns False if unable to satisfy any constraints (and reverts structure to its original), true else
		"""

		if types_list == None:
			types_list = []

		sites_copy = copy.deepcopy(self.sites)

		for site in self.sites:

			if site['type'] not in types_list:
				continue

			if enforced_minimum_atomic_distance:
				success = self.randomly_displace_site_position_with_minimum_distance_constraints(site, stdev, enforced_minimum_atomic_distance, max_displacement_distance, mean)

				if not success:
					self.sites = sites_copy #restore structure to original form
					return False
			else:
				self.randomly_displace_site_position(site, stdev, max_displacement_distance, mean)

		return True

	def randomly_displace_site_position_with_minimum_distance_constraints(self, site, stdev, enforced_minimum_atomic_distance, max_displacement_distance=None, mean=0.0, max_attempt_count=400):
		"""
		Calls randomly_displace_site_position for a site. Tries until no atoms are within enforced_minimum_atomic_distance (angstroms) of the atom being perturbed.
		Maxes out after a finite number of tries (returns false)
		"""

		original_position = copy.deepcopy(site['position'])

		for attempt_count in range(max_attempt_count):
			self.randomly_displace_site_position(site, stdev, max_displacement_distance, mean)

			if self.any_sites_are_too_close_to_site(site, enforced_minimum_atomic_distance):
				site['position'] = copy.deepcopy(original_position)
				continue
			else:
				return True

		return False

	def randomly_displace_site_position(self, site, stdev, max_displacement_distance=None, mean=0.0):
		"""
		Randomly displaces a single site in separate random directions with
		displacement magnitude governed by a normal distribution.
		!!Parameters are given in angstroms!!
		Site will be converted to direct coordinates for sites represented
		in direct coordinates. Modifies site.
		"""

		if max_displacement_distance and max_displacement_distance < 0.0:
			raise Exception("Max displacement distance must be a non-negative quantity")

		displacement_vector = Vector.get_random_vector(mean, stdev) #vector is in angstroms

		if max_displacement_distance and (displacement_vector.magnitude > max_displacement_distance):
			corrector_fraction = max_displacement_distance/displacement_vector.magnitude
			displacement_vector = displacement_vector * corrector_fraction

		if site['coordinate_mode'] == 'Direct':
			#convert disp vec to direct coordinates
			displacement_vector = Vector.get_in_direct_coordinates(displacement_vector, self.lattice)

		site.displace(displacement_vector)


	def get_random_structure(self, population_of_last_generation):

		A_type = self.ga_input_dictionary['species_list'][0]
		B_type = self.ga_input_dictionary['species_list'][1]
		X_type = self.ga_input_dictionary['species_list'][2]

		Nx = self.ga_input_dictionary['supercell_dimensions_list'][0]
		Ny = self.ga_input_dictionary['supercell_dimensions_list'][1]
		Nz = self.ga_input_dictionary['supercell_dimensions_list'][2]

		a = self.ga_input_dictionary['epitaxial_lattice_constant']
		unit_cell_a = a/Nx

		c = ( a * Nz ) / Nx ##############################eventually base c off of a good volume

		lattice = [[a, 0.0, 0.0], [0.0, a, 0.0], [0.0, 0.0, c]]

		structure = Perovskite(supercell_dimensions=self.ga_input_dictionary['supercell_dimensions_list'], lattice=lattice, species_list=self.ga_input_dictionary['species_list'])



		
		probabilities_list = [0.1, 0.6, 0.3]
		random_selector = RandomSelector(probabilities_list)
		event_index = random_selector.get_event_index()


		minimum_atomic_distance_list = [1.5, 1.5, 1.3]
		#The direction of displacement is always spherically uniformly distributed, but we can control the
		#mean radius of this sphere, the standard deviation of this sphere radius, and the max limiting 
		#outer shell of the sphere. These factors are given for A, B, and O atoms separately.

		if event_index == 0: #very close to perfect perovskite, little strain, mostly B-cation displacements
			shear_factor = 0.2
			strain_stdev = 0.06

			mean_displacement_magnitude_list = [0.0*unit_cell_a, 0.15*unit_cell_a, 0.0*unit_cell_a]
			displacement_stdev_list = [0.1*unit_cell_a, 0.2*unit_cell_a, 0.15*unit_cell_a]
			max_atomic_displacement_list = [0.3*(0.7071*unit_cell_a), 0.7*(0.5*unit_cell_a), 0.4*(0.7071*unit_cell_a)]

			minimum_atomic_distance_list = [1.5, 1.2, 1.2] #this controls the min dist when A is displaced, B is displaced, etc.
		elif event_index == 1: #A lot of displacement all alround, little shear strain
			shear_factor = 0.1
			strain_stdev = 0.08

			mean_displacement_magnitude_list = [0.0*unit_cell_a, 0.0*unit_cell_a, 0.0*unit_cell_a]
			displacement_stdev_list = [0.22*unit_cell_a, 0.4*unit_cell_a, 0.4*unit_cell_a]
			max_atomic_displacement_list = [0.3*(0.7071*unit_cell_a), 1.0*(0.5*unit_cell_a), 0.9*(0.7071*unit_cell_a)]
			minimum_atomic_distance_list = [1.3, 1.2, 1.2]
		elif event_index == 2: #A lot of displacement all around, significant shear
			shear_factor = 0.5
			strain_stdev = 0.12

			mean_displacement_magnitude_list = [0.0*unit_cell_a, 0.0*unit_cell_a, 0.0*unit_cell_a]
			displacement_stdev_list = [0.2*unit_cell_a, 0.45*unit_cell_a, 0.45*unit_cell_a]
			max_atomic_displacement_list = [0.3*(0.7071*unit_cell_a), 1.0*(0.5*unit_cell_a), 0.9*(0.7071*unit_cell_a)]
			minimum_atomic_distance_list = [1.3, 1.2, 1.2]




		structure.lattice.randomly_strain(stdev=strain_stdev, mask_array=[[0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 1.0]])



		max_x = 10.0

		def envelope_function(curvature_parameter, max_displacement_distance):
			"""
			curvature_parameter: closer to 0 means sharper peak at 0, closer to 3 or more, very constant until sharp drop to 0 at max_disp_dist
			"""

			return lambda x: 1.0 - ((x**curvature_parameter)/(max_displacement_distance**n))


		A_site_vector_magnitude_distribution_function = Distribution(envelope_function(A_site_curvature_parameter, A_site_max_displacement), 0.0, A_site_max_displacement)
		B_site_vector_magnitude_distribution_function = Distribution(envelope_function(B_site_curvature_parameter, B_site_max_displacement), 0.0, B_site_max_displacement)
		X_site_vector_magnitude_distribution_function = Distribution(envelope_function(X_site_curvature_parameter, X_site_max_displacement), 0.0, X_site_max_displacement)

		A_site_vector_distribution_function = VectorDistribution(Vector.get_random_unit_vector, A_site_vector_magnitude_distribution_function)
		B_site_vector_distribution_function = VectorDistribution(Vector.get_random_unit_vector, B_site_vector_magnitude_distribution_function)
		X_site_vector_distribution_function = VectorDistribution(Vector.get_random_unit_vector, X_site_vector_magnitude_distribution_function)

		displacement_vector_distribution_function_dictionary_by_type = {
			A_type: A_site_vector_distribution_function.get_random_vector,
			B_type: B_site_vector_distribution_function.get_random_vector,
			X_type: X_site_vector_distribution_function.get_random_vector
		}

		minimum_atomic_distances_nested_dictionary_by_type = 
		{
			A_type: {A_type: AA_minimum_distance, B_type: AB_minimum_distance, X_type: AX_minimum_distance},
			B_type: {A_type: AB_minimum_distance, B_type: BB_minimum_distance, X_type: BX_minimum_distance},
			X_type: {A_type: AX_minimum_distance, B_type: BX_minimum_distance, X_type: XX_minimum_distance}
		}

		displace_site_positions_with_minimum_distance_constraints(displacement_vector_distribution_function_dictionary_by_type, minimum_atomic_distances_nested_dictionary_by_type)
	


		#iterate through each type (A, B, O) and apply the specific random distributions when displacing
		for i in range(3):
			structure.randomly_displace_site_positions(stdev=displacement_stdev_list[i], enforced_minimum_atomic_distance=minimum_atomic_distance_list[i], 
				max_displacement_distance=max_atomic_displacement_list[i], mean=mean_displacement_magnitude_list[i], types_list=self.ga_input_dictionary['species_list'][i])
		

		self.structure_creation_id_string = 'random_standard_type_' + str(event_index)
		self.parent_structures_list = None

		return structure
