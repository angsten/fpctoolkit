import copy

from fpctoolkit.util.vector import Vector

class SiteMapping(object):
	"""
	Maps single site to another site, tracking site instances and their indices in collections
	"""

	def __init__(self, initial_site, final_site, lattice=None, initial_index=None, final_index=None):
		self.initial_site = copy.deepcopy(initial_site)
		self.final_site = copy.deepcopy(final_site)
		self.initial_index = initial_index
		self.final_index = final_index

		if lattice:
			distance_and_displacement_vector = self.get_distance_and_displacement_vector(lattice)
			self.distance = distance_and_displacement_vector[0]
			self.displacement_vector = distance_and_displacement_vector[1]


	def get_distance_and_displacement_vector(self, lattice):

		self.initial_site.convert_to_direct_coordinates(lattice)
		self.final_site.convert_to_direct_coordinates(lattice)

		return Vector.get_minimum_distance_between_two_periodic_points(fractional_coordinate_1, fractional_coordinate_2, lattice, N_max=3, return_vector=False)
