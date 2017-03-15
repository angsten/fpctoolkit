#from fpctoolkit.structure.structure_breeder import StructureBreeder

from fpctoolkit.structure.perovskite import Perovskite



class StructureBreeder(object):
	"""
	Defines static methods useful for mating structures together to produce a new structure. These methods fall into two categories:

	1. Methods that return functions that, when called like f(structure_1, structure_2), return new mated structure.
	2. Helper methods for creating the functions of the first type.
	"""

	@staticmethod
	def get_perovskite_mating_function(supercell_dimensions_list):
		"""
		Returns a function that, when called with two structures as its arguments, returns a mated perovskite structure.
		"""

		def mating_function(structure_1, structure_2):
			return StructureBreeder.get_mated_perovskite_structure(structure_1, structure_2, supercell_dimensions_list)

		return mating_function

	@staticmethod
	def get_mated_perovskite_structure(structure_1, structure_2, supercell_dimensions_list):

		#validation: check that species are the same in each structure
		#########need to add min atomic distance check!!!!!!!!!!!!!!!!!!!!!!!!!!!

		Na = supercell_dimensions_list[0]
		Nb = supercell_dimensions_list[1]
		Nc = supercell_dimensions_list[2]

		parent_structures_list = [structure_1, structure_2]

		#everything below should be factored out into a function that takes in two structures (and interpolators) and returns one

		site_mapping_collections_list = []

		for i, parent_structure in enumerate(parent_structures_list):
			print "Parent structure " + str(i+1)

			perovskite_reference_structure = Perovskite(supercell_dimensions=supercell_dimensions_list, lattice=parent_structure.lattice, species_list=parent_structure.get_species_list())

			perovskite_reference_structure.convert_sites_to_direct_coordinates()
			parent_structure.convert_sites_to_direct_coordinates()

			parent_structure.sites.shift_direct_coordinates([random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)])


			#This aligns the lattices - sloppy but it works...figure out a better way later
			for align_try_count in range(21):
				if align_try_count == 20:
					raise Exception("Cannot align crystal to perfect perovskite")

				site_mapping_collection = SiteMappingCollection(perovskite_reference_structure.sites, parent_structure.sites, lattice=parent_structure.lattice)
				average_displacement_vector = site_mapping_collection.get_average_displacement_vector()
				print average_displacement_vector
				site_mapping_collection.shift_sites_to_minimize_average_distance() #this shifts parent_struct's sites too because sites passed by reference

				converged = True
				for j in range(3):
					if abs(average_displacement_vector[j]) > 0.00001:
						converged = False

				if converged:
					break

			site_mapping_collections_list.append(site_mapping_collection)



		#This should be a separately inputted block controlling how interpolation is run##################
		if Na == 2:
			discrete_interpolation_values = [1.0, 1.0, 0.0, 0.0] #one for each plane of perov atoms
		if Na == 4:
			discrete_interpolation_values = [1.0, 1.0, 1.0, 0.8, 0.0, 0.0, 0.0, 0.2]

		def interpolation_function_da(da, db, dc):
			transition_increment = 0.5/Na #distance between perf perov planes in a direction
			transition_index = int(da/transition_increment)

			return discrete_interpolation_values[transition_index]

		def interpolation_function_db(da, db, dc):
			return interpolation_function_da(db, da, dc)

		def interpolation_function_dc(da, db, dc):
			return interpolation_function_da(dc, da, db)

		if random.uniform(0.0, 1.0) >= 0.5:
			interpolation_function_1 = interpolation_function_da
		else:
			interpolation_function_1 = interpolation_function_db

		if Na == 2 and Nc == 2:
			if random.uniform(0.0, 1.0) >= 0.66666:
				interpolation_function_1 = interpolation_function_dc	


		def interpolation_function_2(da, db, dc):
			return 1.0 - interpolation_function_1(da, db, dc)
		###################################################################################


		#make this a randomly weighted-average at some point
		averaged_lattice = Lattice.average(parent_structures_list[0].lattice, parent_structures_list[1].lattice)

		interpolated_sites_1 = site_mapping_collections_list[0].get_interpolated_site_collection(perovskite_reference_structure.sites, interpolation_function_1)
		interp_struct_1 = Structure(sites=interpolated_sites_1, lattice=averaged_lattice)

		interpolated_sites_2 = site_mapping_collections_list[1].get_interpolated_site_collection(interpolated_sites_1, interpolation_function_2)

		interp_struct_2 = Structure(sites=interpolated_sites_2, lattice=averaged_lattice)

		return interp_struct_2