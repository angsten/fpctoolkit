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