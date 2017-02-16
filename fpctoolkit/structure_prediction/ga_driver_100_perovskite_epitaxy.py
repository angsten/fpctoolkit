import copy

from fpctoolkit.structure_prediction.ga_driver import GADriver
from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.structure_prediction.individual import Individual

class GADriver100PerovskiteEpitaxy(GADriver):


	def __init__(self, ga_input_dictionary, calculation_set_input_dictionary):
		"""
			ga_input_dictionary should additionally have species_list, epitaxial_lattice_constant (full number, not 5-atom cell equivalent),
			and supercell_dimensions_list keys and values
		"""

		super(GADriver100PerovskiteEpitaxy, self).__init__(ga_input_dictionary, calculation_set_input_dictionary)

		self.structure_creation_id_string = 'none' #will track how the individual's structure was created
		self.parent_structures_list = None

		if not (self.ga_input_dictionary['supercell_dimensions_list'][0] == self.ga_input_dictionary['supercell_dimensions_list'][1]):
			raise Exception("For (100) epitaxial conditions, Nx must = Ny supercell dimensions. Other behavior not yet supported")


	def get_new_individual(self, individual_path, population_of_last_generation, generation_number):
		"""
		Main workhorse - supplies an individual by randomly chosen means (heredity, random, mutate, ...etc.)
		"""

		initial_structure = self.get_structure(population_of_last_generation, generation_number)

		relaxation = VaspRelaxation(path=individual_path, initial_structure=initial_structure, input_dictionary=copy.deepcopy(self.calculation_set_input_dictionary))

		#package this with path and input_dict in calc set (relax) and return as individual

		return Individual(calculation_set=relaxation, structure_creation_id_string=self.structure_creation_id_string, parent_structures_list=self.parent_structures_list)

	def get_random_structure(self, population_of_last_generation):
		a = self.ga_input_dictionary['epitaxial_lattice_constant']

		Nx = self.ga_input_dictionary['supercell_dimensions_list'][0]
		Nz = self.ga_input_dictionary['supercell_dimensions_list'][2]

		c = ( a * Nz ) / Nx ##############################eventually base c off of a good volume

		lattice = [[a, 0.0, 0.0], [0.0, a, 0.0], [0.0, 0.0, c]]

		structure = Perovskite(supercell_dimensions=self.ga_input_dictionary['supercell_dimensions_list'], lattice=lattice, species_list=self.ga_input_dictionary['species_list'])

		shear_factor = 0.8
		structure.lattice.randomly_strain(stdev=0.06, mask_array=[[0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 1.0]]) #for (100) epitaxy

		mult = 2.5
		min_atomic_distance = 1.5
		structure.randomly_displace_site_positions(stdev=0.2*mult, enforced_minimum_atomic_distance=min_atomic_distance, max_displacement_distance=0.3*mult, mean=0.3, types_list=['K'])
		structure.randomly_displace_site_positions(stdev=0.6*mult, enforced_minimum_atomic_distance=min_atomic_distance, max_displacement_distance=0.6*mult, mean=0.5, types_list=['V'])
		structure.randomly_displace_site_positions(stdev=0.8*mult, enforced_minimum_atomic_distance=min_atomic_distance, max_displacement_distance=1.2*mult, mean=0.7, types_list=['O'])

		self.structure_creation_id_string = 'random_standard'
		self.parent_structures_list = None

		return structure





	def get_mated_structure(self, population_of_last_generation):

		#select parents from population first

		parent_structure_1 = Structure(lattice=[[4.0, 0.0, 0.0], [0.0, 4.0, 0.0], [0.0, 0.0, 4.0]], sites=SiteCollection([Site({'type':'Ba', 'coordinate_mode': 'Direct', 'position':[0.0, 0.0, 0.0]})]))

		