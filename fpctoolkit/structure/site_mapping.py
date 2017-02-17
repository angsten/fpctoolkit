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
		else:
			self.distance = None
			self.displacement_vector = None

	def __str__(self):
		out_string = ""

		out_string = " ".join(str(x) for x in (self.initial_site['position'], '->', self.final_site['position'], ' distance:', self.distance, ' direction:', self.displacement_vector))

		return out_string

	def __repr__(self):
		return str(self)

	def get_distance_and_displacement_vector(self, lattice):

		self.initial_site.convert_to_direct_coordinates(lattice)
		self.final_site.convert_to_direct_coordinates(lattice)

		return Vector.get_minimum_distance_between_two_periodic_points(self.initial_site['position'], self.final_site['position'], lattice, return_vector=True)

