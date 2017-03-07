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
