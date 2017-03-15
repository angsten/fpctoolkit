#from fpctoolkit.structure.structure_manipulator import StructureManipulator



from fpctoolkit.structure.structure import Structure



class StructureManipulator(object):
	"""
	Defines static methods useful for modifying (or getting modified versions of) structures in some way, such as displacing site positions.
	"""

	@staticmethod
	def get_supercell(structure, supercell_dimensions_list):
		"""
		Returns a new structure that is a supercell structure (structure is not modified)
		Argument supercell_dimensions_list could look like [1,3,4].
		"""

		Structure.validate(structure)


		if not len(supercell_dimensions_list) == 3:
			raise Exception("Argument supercell_dimensions_list must be of length 3")

		for dimension in supercell_dimensions_list:
			if not int(dimension) == dimension:
				raise Exception("Only integer values accepted for supercell dimension factors.")

		structure.convert_sites_to_direct_coordinates()

		new_lattice = structure.lattice.get_super_lattice(supercell_dimensions_list)
		new_sites = SiteCollection()

		for original_site in structure.sites:
			for a in range(supercell_dimensions_list[0]):
				for b in range(supercell_dimensions_list[1]):
					for c in range(supercell_dimensions_list[2]):
						a_frac = float(a)/float(supercell_dimensions_list[0])
						b_frac = float(b)/float(supercell_dimensions_list[1])
						c_frac = float(c)/float(supercell_dimensions_list[2])

						new_site = copy.deepcopy(original_site)
						old_position = original_site['position']
						new_site['position'] = [old_position[0]/supercell_dimensions_list[0]+a_frac, old_position[1]/supercell_dimensions_list[1]+b_frac, old_position[2]/supercell_dimensions_list[2]+c_frac]
						new_sites.append(new_site)


		return Structure(lattice=new_lattice, sites=new_sites)


	@staticmethod	
	def displace_site_positions_with_minimum_distance_constraints(structure, displacement_vector_distribution_function_dictionary_by_type=None, minimum_atomic_distances_nested_dictionary_by_type=None):
		"""
		Displace the atoms of structure using the specified probability distribution functions for each atom type (modifies in place).

		Algorithm:
		1. Randomly displace sites according to the given distribution funcitons for each type.
		2. For those atoms that are too close under p.b.c. (as defined in the minimum distance matrix), randomly choose on of the 'collided' 
		   pair and re-displace according to its distribution function.
		3. Repeat until no two atoms are too close.

		displacement_vector_distribution_function_dictionary_by_type should look like:
		{
			'Ba': dist_func_1, #dist funcs are methods that return cartesian vectors in angstroms ([x, y, z]) using distributions of your choosing
			'Ti': dist_func_2,
			...
		}

		minimum_atomic_distances_nested_dictionary_by_type is in angstroms and looks like:
		{
			'Ba': {'Ba': 1.5, 'Ti': 1.2, 'O': 1.4},
			'Ti': {'Ba': 1.2, 'Ti': 1.3, 'O': 1.3},
			'O':  {'Ba': 1.4, 'Ti': 1.3, 'O': 0.8}
		}

		Calling any of the dist_funcs must return a displacement vector that uses cartesian coordinates and angstroms as its units. 
		If no function is given for a type, the zero vector function is used.

		This method should approximately preserve the overall distribution rho(x1, y1, z1, x2, y2, z2, ...) resulting from multiplication
		of the indiviidual independent atomic distributions but with the regions of atoms too close (distance < min_atomic_dist) set to rho = 0.
		This just renormalizes the other parts of the distribution space so integral of rho sums to unity.
		"""

		Structure.validate(structure)

		original_structure = copy.deepcopy(structure)
		original_sites_list = copy.deepcopy(structure.sites.get_sorted_list())
		new_sites_list = structure.sites.get_sorted_list()

		sites_to_check_indices_list = range(len(new_sites_list))

		Structure.displace_site_positions(structure, displacement_vector_distribution_function_dictionary_by_type)

		for try_count in range(200):

			indices_of_site_pairs_that_are_too_close_list = structure.get_indices_of_site_pairs_that_are_too_close_to_sites_list(sites_to_check_indices_list, minimum_atomic_distances_nested_dictionary_by_type)
			sites_to_check_indices_list = []
			indices_to_displace_list = []

			if indices_of_site_pairs_that_are_too_close_list != []:
				print indices_of_site_pairs_that_are_too_close_list

				for (site_1_index, site_2_index) in indices_of_site_pairs_that_are_too_close_list:
					probabilities_list = [0.5, 0.5]
					random_selector = RandomSelector(probabilities_list)
					event_index = random_selector.get_event_index()

					if event_index == 0:
						index_to_displace = site_1_index
					else:
						index_to_displace = site_2_index

					print "moving randomly selected index " + str(index_to_displace) + " of pair " + str((site_1_index, site_2_index))

					if index_to_displace in indices_to_displace_list:
						print "already in index list of sites that have been moved"
						continue

					new_sites_list[index_to_displace]['coordinate_mode'] = original_sites_list[index_to_displace]['coordinate_mode']
					new_sites_list[index_to_displace]['position'] = copy.deepcopy(original_sites_list[index_to_displace]['position'])

					new_sites_list[index_to_displace].randomly_displace(displacement_vector_distribution_function_dictionary_by_type, structure.lattice)
					sites_to_check_indices_list.append(index_to_displace)
					indices_to_displace_list.append(index_to_displace)

			else:
				return


		raise Exception("Could not displace this structure while satisfying the given constraints")


	@staticmethod
	def displace_site_positions(structure, displacement_vector_distribution_function_dictionary_by_type=None):
		"""
		Inner loop helper function for displace_site_positions_with_minimum_distance_constraint
		"""

		Structure.validate(structure)

		if (displacement_vector_distribution_function_dictionary_by_type == None) or len(displacement_vector_distribution_function_dictionary_by_type) == 0:
			raise Exception("A displacement vector function for at least one atom type must be specified.")

		for species_type in displacement_vector_distribution_function_dictionary_by_type:
			if not species_type in structure.sites.keys():
				raise Exception("Strucuture does not have a site of type " + str(species_type))

		#If a distribution function is not provided for a given type, set that type's function to the zero vector function
		for species_type in structure.sites.keys():
			if not species_type in displacement_vector_distribution_function_dictionary_by_type:
				displacement_vector_distribution_function_dictionary_by_type[species_type] = lambda: [0, 0, 0]


		for species_type in structure.sites.keys():
			for site in structure.sites[species_type]:
				site.randomly_displace(displacement_vector_distribution_function_dictionary_by_type[site['type']], structure.lattice)
