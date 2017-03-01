import random

import fpctoolkit.util.string_util as su
from fpctoolkit.io.file import File
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.potcar import Potcar
from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.io.vasp.incar import Incar
from fpctoolkit.util.path import Path
from fpctoolkit.structure.site import Site
from fpctoolkit.structure.lattice import Lattice
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.structure.site_collection import SiteCollection
from fpctoolkit.io.vasp.outcar import Outcar
from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.util.vector import Vector
from fpctoolkit.structure_prediction.ga_structure_predictor import GAStructurePredictor
from fpctoolkit.structure_prediction.ga_driver_100_perovskite_epitaxy import GADriver100PerovskiteEpitaxy
from fpctoolkit.structure_prediction.population import Population
from fpctoolkit.util.distribution import Distribution
from fpctoolkit.util.vector_distribution import VectorDistribution


max_x = 10.0

def func(x, n, max_x):
	return 1.0 - ((x**n)/(max_x**n))

def dist_func(x):
	return func(x, 0.1, max_x)

dist = Distribution(dist_func, 0.0, max_x)

magnitude_dist_function = dist.get_random_value
direction_dist_function = Vector.get_random_unit_vector

vdist = VectorDistribution(direction_dist_function, magnitude_dist_function)

for i in range(100):
	print vdist.get_random_vector()



# def dist_func(x):
# 	if x < 1.0:
# 		return 0.0

# 	if x > 2.0 and x < 5.0:
# 		return 0.0

# 	return x**6

# dist = Distribution(dist_func, 0.0, 6.0)

# l = []
# sample_size = 1000000
# for i in range(sample_size):
# 	l.append(dist.get_random_value())


# count = 0
# for i in range(len(l)):
# 	if l[i] < 2.0:
# 		count += 1

# print count
# print "Expected: ", 0.000629302*sample_size


# ga_path = "C:\Users\Tom\Documents\Coding\python_work\workflow_test\ga_test"
# Path.remove(ga_path)

# calculation_set_input_dictionary = {
# 	'external_relaxation_count': 1,
# 	'kpoint_schemes_list': ['Monkhorst'],
# 	'kpoint_subdivisions_lists': [[2, 2, 2]],
# 	'submission_script_modification_keys_list': ['100'],
# 	'submission_node_count_list': [1],
# 	'ediff': [0.001],
# 	'encut': [400]
# }

# ga_input_dictionary = {
# 	'species_list':['K', 'V', 'O'],
# 	'epitaxial_lattice_constant': 15.16,
# 	'supercell_dimensions_list': [4, 4, 1],
# 	'max_number_of_generations': 1,
# 	'individuals_per_generation': [3],
# 	'random_fractions_list': [1.0, 0.3, 0.2],
# 	'mate_fractions_list': [0.0, 0.7, 0.8]
# }

# ga_driver = GADriver100PerovskiteEpitaxy(ga_input_dictionary, calculation_set_input_dictionary)

# # ga_structure_predictor = GAStructurePredictor(ga_path, ga_driver)

# # ga_structure_predictor.update()

# #ga_driver.get_mated_structure(None)

# def func():
# 	return None

# struct = Structure(file_path="C:\Users\Tom\Documents\Coding\python_work\workflow_test/20_atom_parent_1.vasp")

# pop = Population(directory_to_individual_conversion_method=func)

# pop.individuals = []







# a = 6
# b = 4
# c = 2
# structure = Perovskite(supercell_dimensions = [a, b, c], lattice=[[4.0*a, 0.0, 0.0], [0.0, 4.0*b, 0.0], [0.0, 0.0, 5.0*c]], species_list=['Sr', 'Ti', 'O'])

# structure.to_poscar_file_path("C:\Users\Tom\Documents\Berkeley/research\Presentation Slides/tms_spring_17_files/substrate.vasp")

# structure = Perovskite(supercell_dimensions = [1, 1, 1], lattice=[[4.8, 0.0, 0.0], [0.0, 4.8, 0.0], [0.0, 0.0, 3.5]], species_list=['Sr', 'Ti', 'O'])

# structure.to_poscar_file_path("C:\Users\Tom\Documents\Berkeley/research\Presentation Slides/tms_spring_17_files/film_5_atom.vasp")


# for i in range(6):
# 	structure = ga_driver.get_random_structure(None)
# 	print ga_driver.structure_creation_id_string
# 	structure.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs/rand_made_"+ga_driver.structure_creation_id_string+"_"+str(i)+".vasp")







class self_c:
	def __init__(self):
		data_path = ""

	def assertEqual(self, left_arg, right_arg = None):
		if not right_arg:
			print left_arg
		else:
			print left_arg == right_arg

	def assertTrue(self, cond):
		print cond

def get_string(printed):
	out_str = '"'
	for line in printed:
		out_str += line + r'\n'
	return out_str + '"'

self = self_c()

#self.data_path = "C:/Users/Tom/Documents/Berkeley/research/scripts/fpctoolkit/fpctoolkit/structure/tests/data_structure/"
# self.data_path = "C:\Users\Tom\Documents\Coding\python_work\workflow_test"
# #self.data_path = "~/workflow_test/"

# convergence_base_path = Path.clean(self.data_path)
# Path.make(convergence_base_path)


# path = Path.join(convergence_base_path, 'relaxation')
# #initial_structure = Perovskite(supercell_dimensions=[4, 4, 1], lattice=[[14.4, 0.0, 0.0], [0.0, 14.4, 0.0], [0.0, 0.0, 5.2]], species_list=['K', 'V', 'O'])
# #initial_structure.randomly_displace_site_positions(0.25)
# initial_structure = Perovskite(supercell_dimensions = [2, 2, 2], lattice=[[8.0, 0.0, 0.0], [0.0, 8.0, 0.0], [0.0, 0.0, 8.0]], species_list=['Ba', 'Ti', 'O'])

# input_dictionary = {
#     'submission_script_modification_keys_list': ['100'],
#     'external_relaxation_count': 10,
#     'kpoint_schemes_list': ['Monkhorst'],
#     'kpoint_subdivisions_lists': [[1, 1, 2], [1, 1, 2], [1, 1, 4]],
#     'ediff': [0.005, 0.005, 0.0001, 0.0001, 0.00005, 0.00005, 0.00001, 0.00001, 0.000001, 0.000001],
#     #'ediffg': [0.001, 0.001, 0.0001, 0.0001, 0.00001, 0.00001],
#     'encut': [300, 300, 400, 400, 500]
# }


# relax = VaspRelaxation(path, initial_structure, input_dictionary)
# relax.update()
# relax.view()


# base_kpoints_scheme = 'Monkhorst'
# base_kpoints_subdivisions_list = [4, 4, 4]
# base_encut = 800
# base_ediff = 0.000001
# base_structure = Perovskite(supercell_dimensions = [2, 2, 2], lattice=[[8.0, 0.0, 0.0], [0.0, 8.0, 0.0], [0.0, 0.0, 8.0]], species_list=['Ba', 'Ti', 'O'])

# convergence_encuts_list = [100]

# encut_convergence_set_path = Path.join(convergence_base_path, 'encut_convergence_set')
# Path.make(encut_convergence_set_path)

# for encut in convergence_encuts_list:
# 	run_path = Path.join(encut_convergence_set_path, str(encut))

# 	kpoints = Kpoints(scheme_string=base_kpoints_scheme, subdivisions_list=base_kpoints_subdivisions_list)
# 	incar = IncarMaker.get_static_incar({'ediff':base_ediff, 'encut':encut})
# 	input_set = VaspInputSet(base_structure, kpoints, incar)

# 	vasp_run = VaspRun(run_path, input_set=input_set)

# 	vasp_run.update()
	#print vasp_run
	#vasp_run.view()




# outcar = Outcar("C:/Users/Tom/Documents/Berkeley/research/scripts/fpctoolkit/fpctoolkit/io/vasp/tests/data_Outcar/outcar")
# print outcar.energy
# print outcar.get_number_of_atoms()
# print outcar.energy_per_atom

# lattice = Lattice(a=[1.0, 0.0, 0.0], b=[0.0, 1.0, 0.0], c=[0.0, 0.0, 1.0])
# #lattice.strain([[2.0, 0.1, 0.1], [0.0, 0.5, 0.1], [0.0, 0.0, 3.0]])
# lattice.strain([1.0, 1.0, 1.0, 0.0, -0.1, 0.0])
# #print lattice

# lattice = Lattice(a=[4.5, 1.0, 0.0], b=[1.0, -4.0, 0.1], c=[-2.0, 1.2, 4.0])
# lattice.strain([[-0.2, -0.05, 0.5], [-0.05, 1.0, 0.5], [0.5, 0.5, 1.0]])
# #print lattice


# lattice = Lattice(a=[1.0, 0.0, 0.0], b=[0.0, 1.0, 0.0], c=[0.0, 0.0, 1.0])
# lattice.randomly_strain(0.1, mask_array=[[1.0, 0.0, 2.0], [0.0, 1.0, 2.0], [0.0, 0.0, 1.0]]) #for (100) epitaxy
# print lattice



# structure = Structure(file_path = "C:/Users/Tom/Documents/Berkeley/research/scripts/fpctoolkit/fpctoolkit/io/vasp/tests/data_Poscar/poscar_small")
# print structure

# structure.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs\orig.vasp")

# structure = structure.get_supercell([2,3,4])

# print structure
# structure.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs\super.vasp")



# for i in range(400):

# position_1 = [0.9422665545626425, -0.2517860326278374, -0.6958826837443033]#[random.uniform(-2.5, 2.5), random.uniform(-2.5, 2.5), random.uniform(-2.5, 2.5)]
# position_2 = [-0.5027141823998538, 2.4234172864246624, 2.0401555768756516]#[random.uniform(-2.5, 2.5), random.uniform(-2.5, 2.5), random.uniform(-2.5, 2.5)]
# print position_1
# print position_2
# #lattice=[[random.uniform(-5.0, 5.0), random.uniform(-5.0, 5.0), random.uniform(-5.0, 5.0)], [random.uniform(-5.0, 5.0), random.uniform(-5.0, 5.0), random.uniform(-5.0, 5.0)], [random.uniform(-5.0, 5.0), random.uniform(-5.0, 5.0), random.uniform(-5.0, 5.0)]]

# #lattice=[[14.4, 0.0, 0.0],[0.0, 14.4, 0.0], [random.uniform(-4.0, 4.0), random.uniform(-4.0, 4.0), random.uniform(4.0, 16.0)]]

# lattice = [[2.576367, -1.48291388128, -0.880068632348], [0.850487776997, 1.06646115307, 1.21942862744], [1.99347821842, 3.27132357289, 4.44781854544]]

# print "Lattice:"
# print Lattice(lattice)



# print Vector.get_minimum_distance_between_two_periodic_points(position_1, position_2, lattice, 5, True)
# print '\n\n'
# print Vector.get_min(position_1, position_2, lattice, 5, True)

#struct = Structure(lattice=lattice, sites=SiteCollection([Site({'type':'Ba', 'coordinate_mode': 'Direct', 'position':position_1}), Site({'type':'Ti', 'coordinate_mode': 'Direct', 'position':position_2})]))

#struct.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs\dist.vasp")

# a = 15.16
# structure = Perovskite(supercell_dimensions = [4, 4, 1], lattice=[[a, 0.0, 0.0], [0.0, a, 0.0], [0.0, 0.0, a/4.0]], species_list=['K', 'V', 'O'])

# shear_factor = 1.0
# structure.lattice.randomly_strain(stdev=0.06, mask_array=[[0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 1.0]]) #for (100) epitaxy

# mult = 1.8
# min_atomic_distance = 1.5
# print structure.randomly_displace_site_positions(stdev=0.2*mult, enforced_minimum_atomic_distance=min_atomic_distance, max_displacement_distance=0.3*mult, mean=0.2, types_list=['K'])
# print structure.randomly_displace_site_positions(stdev=0.6*mult, enforced_minimum_atomic_distance=min_atomic_distance, max_displacement_distance=0.6*mult, mean=0.4, types_list=['V'])
# print structure.randomly_displace_site_positions(stdev=0.8*mult, enforced_minimum_atomic_distance=min_atomic_distance, max_displacement_distance=1.0*mult, mean=0.6, types_list=['O'])


# structure.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs\dist.vasp")