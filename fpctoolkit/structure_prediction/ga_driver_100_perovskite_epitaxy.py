

from fpctoolkit.structure_prediction.ga_driver import GADriver
from fpctoolkit.structure.perovskite import Perovskite

class GADriver100PerovskiteEpitaxy(GADriver):


	def __init__(self, ga_input_dictionary, calculation_set_input_dictionary):
		"""
			ga_input_dicitonary should additionally have species_list, epitaxial_lattice_constant (full number, not 5-atom cell equivalent),
			and supercell_dimensions_list keys and values
		"""

		super(GADriver100Epitaxy, self).__init__(ga_input_dictionary, calculation_set_input_dictionary)



	def get_random_structure(self):
		a = self.ga_input_dicitonary['epitaxial_lattice_constant']

		Nx = self.ga_input_dicitonary['supercell_dimensions_list'][0]
		Nz = self.ga_input_dicitonary['supercell_dimensions_list'][2]

		c = ( a * Nz ) / Nx ##############################eventually base c off of a good volume

		lattice = [[a, 0.0, 0.0], [0.0, a, 0.0], [0.0, 0.0, c]]

		structure = Perovskite(supercell_dimensions=self.ga_input_dicitonary['supercell_dimensions_list'], lattice=lattice, species_list=self.ga_input_dicitonary['species_list'])

		shear_factor = 0.8
    	structure.lattice.randomly_strain(stdev=0.06, mask_array=[[0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 1.0]]) #for (100) epitaxy

   		mult = 2.5
    	min_atomic_distance = 1.5
    	structure.randomly_displace_site_positions(stdev=0.2*mult, enforced_minimum_atomic_distance=min_atomic_distance, max_displacement_distance=0.3*mult, mean=0.3, types_list=['K'])
    	structure.randomly_displace_site_positions(stdev=0.6*mult, enforced_minimum_atomic_distance=min_atomic_distance, max_displacement_distance=0.6*mult, mean=0.5, types_list=['V'])
    	structure.randomly_displace_site_positions(stdev=0.8*mult, enforced_minimum_atomic_distance=min_atomic_distance, max_displacement_distance=1.2*mult, mean=0.7, types_list=['O'])

		return structure





	def get_mated_structure(self):
		pass