import random
import numpy as np
import sys

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
from fpctoolkit.util.math.vector import Vector
from fpctoolkit.structure_prediction.ga_structure_predictor import GAStructurePredictor
from fpctoolkit.structure_prediction.ga_driver import GADriver
from fpctoolkit.structure_prediction.population import Population
from fpctoolkit.util.math.distribution import Distribution
from fpctoolkit.util.math.vector_distribution import VectorDistribution
from fpctoolkit.structure_prediction.selector import Selector
from fpctoolkit.structure.structure_breeder import StructureBreeder
from fpctoolkit.structure.structure_generator import StructureGenerator
from fpctoolkit.structure.site_mapping_collection import SiteMappingCollection
from fpctoolkit.util.math.distribution_array import DistributionArray
from fpctoolkit.util.math.distribution_generator import DistributionGenerator
import fpctoolkit.util.phonopy_interface.phonopy_utility as phonopy_utility
from fpctoolkit.phonon.phonon_structure import PhononStructure
from fpctoolkit.phonon.normal_mode import NormalMode
from fpctoolkit.structure.displacement_vector import DisplacementVector
from fpctoolkit.phonon.hessian import Hessian
from fpctoolkit.phonon.eigen_structure import EigenStructure




a = 3.79
Nx = 1
Ny = 1
Nz = 1


base_path = "C:\Users\Tom\Documents\Berkeley/research\my_papers\Epitaxial Phase Validation Paper\phonon_work/"

outcar = Outcar(Path.join(base_path, 'OUTCAR_small_refined'))
hessian = Hessian(outcar)



reference_structure=Perovskite(supercell_dimensions=[Nx, Ny, Nz], lattice=[[a*Nx, 0.0, 0.0], [0.0, a*Ny, 0.0], [0.0, 0.0, a*Nz]], species_list=['Sr', 'Ti', 'O'])

relaxed_struct = Structure("C:\Users\Tom\Desktop\Vesta_Inputs/rel_sr_ti.vasp")
print relaxed_struct
print
eigen_structure = EigenStructure(reference_structure=reference_structure, hessian=hessian, distorted_structure=relaxed_struct)
print eigen_structure


relaxed_struct.sites[0]['position'][2] = -0.000204


print relaxed_struct
print
eigen_structure = EigenStructure(reference_structure=reference_structure, hessian=hessian, distorted_structure=relaxed_struct)
print eigen_structure


# dist_structure = eigen_structure.get_distorted_structure()

# dist_structure.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs/rel_sr_ti_reproduced.vasp")

# dist_eigen_structure = EigenStructure(reference_structure=reference_structure, hessian=hessian, distorted_structure=dist_structure)
# print dist_eigen_structure 


# component_index = 0
# eigen_structure[component_index+6] = 1.0

# component_index = 1
# eigen_structure[component_index+6] = 1.4355

# component_index = 5
# eigen_structure[component_index+6] = -0.111



# for i in range(len(eigen_structure)):
# 	if i <= 5:
# 		# if (i in [0, 1, 5]):
# 		# 	continue

# 		eigen_structure[i] = random.uniform(-0.3, 0.3)
# 	else:
# 		eigen_structure[i] = random.uniform(-1.0, 1.0)


# for i in range(len(eigen_structure)):
# 	if i >= 6 and i <= (120+5):
# 		if (i in [12, 13, 14]):
# 			continue
# 			# eigen_structure[i] = random.uniform(-1.5, 1.5)
# 		else:
# 			eigen_structure[i] = random.uniform(-0.35, 0.35)

# chrom = [0.01875, 0.01872, 0.01869, 1e-05, 1e-05, 3e-05, -0.54132, 1.90443, -1.34194, 0.06017, -0.00184, 1.98603, -0.0001, -0.00015, 0.00026, 0.1911,  -2.87686,  -0.08586,  -0.93214, -0.00041, 3.14068]

# eigen_structure.set_eigen_chromosome(chrom)

# # print eigen_structure
# #print eigen_structure.eigen_components_list[component_index]
# # eigen_structure.print_eigen_components()

# distorted_structure = eigen_structure.get_distorted_structure()

# distorted_structure.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs/dist_fc.vasp")


# dist_eig_struct = EigenStructure(reference_structure=reference_structure, hessian=hessian, distorted_structure=distorted_structure)

# print eigen_structure
# print
# print dist_eig_struct


# # for i in range(len(eigen_structure)):
# # 	if abs(eigen_structure[i] - dist_eig_struct[i]) > 1e-8:
# # 		raise Exception("Components not equal for component", i, eigen_structure[i], dist_eig_struct[i])

# #dist_eig_struct.set_translational_eigen_component_amplitudes_to_zero()
# dist_2_struct = dist_eig_struct.get_distorted_structure()
# dist_2_struct.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs/dist_fc_eig_repro.vasp")



# struct = Structure("C:\Users\Tom\Desktop\Vesta_Inputs/rel_sr_ti_mod.vasp")
# rel_eig_struct = EigenStructure(reference_structure=reference_structure, hessian=hessian, distorted_structure=struct)
# print
# print rel_eig_struct

# rel_struct = dist_eig_struct.get_distorted_structure()
# rel_struct.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs/dist_fc_eig_repro_relaxed_mod.vasp")

################################################################################################################force const stuff#####################################################








# a = 3.79
# Nx = 2
# Ny = 2
# Nz = 2


# initial_structure=Perovskite(supercell_dimensions=[Nx, Ny, Nz], lattice=[[a*Nx, 0.0, 0.0], [0.0, a*Ny, 0.0], [0.0, 0.0, a*Nz]], species_list=['Sr', 'Ti', 'O'])




# symmetrized = False

# def symmetrize(a):
#     return (a + a.T)/2.0

# def print_eigen_vector(eigen_vector):
# 	f = su.pad_decimal_number_to_fixed_character_length
# 	rnd = 5
# 	pad = 8
# 	for i in range(len(eigen_vector)/3):
# 		print "Atom ", i, f(eigen_vector[3*i+0], rnd, pad),  f(eigen_vector[3*i+1], rnd, pad),  f(eigen_vector[3*i+2], rnd, pad)

# def print_hessian(hessian):
# 	f = su.pad_decimal_number_to_fixed_character_length
# 	rnd = 4
# 	pad = 6

# 	for i in range(len(hessian)):
# 		for j in range(len(hessian)):
# 			print f(hessian[i][j], rnd, pad),
# 		print




# base_path = "C:\Users\Tom\Documents\Berkeley/research\my_papers\Epitaxial Phase Validation Paper\phonon_work/"

# outcar = Outcar(Path.join(base_path, 'OUTCAR_large_refined'))

# np_hess_refined = np.asarray(outcar.get_hessian_matrix())


# if symmetrized:
# 	np_hess_refined = symmetrize(np_hess_refined) #####################enforce symmetry across diagonal

# #print_hessian(np_hess_refined)





# if symmetrized:
# 	eigen_values, eigen_vectors = np.linalg.eigh(np_hess_refined)
# else:
# 	eigen_values, eigen_vectors = np.linalg.eigh(np_hess_refined)




# eigen_value_vector_pairs = []

# for i in range(len(eigen_values)):
# 	eigen_value_vector_pairs.append([eigen_values[i], eigen_vectors[:, i]])

# sorted_eigen_value_vector_pairs = sorted(eigen_value_vector_pairs, key=lambda pair: pair[0])



# eigen_values = []
# eigen_vectors = []

# for i in range(len(sorted_eigen_value_vector_pairs)):
# 	eigen_values.append(sorted_eigen_value_vector_pairs[i][0])
# 	eigen_vectors.append(sorted_eigen_value_vector_pairs[i][1])





# print eigen_values
# # for i in range(len(eigen_values)):
# # 	print '-'*100
# # 	print "Eigenvalue", i, ": ", round(eigen_values[i], 7)
# # 	print_eigen_vector(eigen_vectors[i])



# for i in range(len(eigen_values)):
# 	for j in range(i+1, len(eigen_values)):
# 		dot = np.dot(eigen_vectors[i], eigen_vectors[j])

# 		if abs(dot) > 1e-12:
# 			print dot, i, j





# # print np.linalg.det(np_hess_refined)

# # print reduce(lambda x, y: x*y, eigen_values)






# for i, eig_val in enumerate(eigen_values):

# 	disp_vec = DisplacementVector(reference_structure=initial_structure, coordinate_mode='Cartesian')

# 	disp_vec.set(eigen_vectors[i])



# 	displaced_structure = disp_vec.get_displaced_structure()

# 	eigstr = str(i) + "_" + str(round(eig_val, 4))

# 	displaced_structure.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs/xx_disp_fc_" + eigstr + ".vasp")
















############################################################################################################end force const stuff#####################################################












# for i in range(len(np_hess_refined)):
# 	for j in range(len(np_hess_refined[0])):
# 		print np_hess_refined[i][j] - np_hess_refined[j][i]



# base_path = "C:\Users\Tom\Documents\Berkeley/research\my_papers\Epitaxial Phase Validation Paper\phonon_work/"

# outcar = Outcar(Path.join(base_path, 'OUTCAR'))
# outcar_refined = Outcar(Path.join(base_path, 'OUTCAR_refined'))


# np_hess = np.asarray(outcar.get_hessian_matrix())
# np_hess_refined = np.asarray(outcar_refined.get_hessian_matrix())


# difference_hessian = np.absolute(np_hess-np_hess_refined)

# percent_change_hessian = 100.0*(difference_hessian/np.absolute(np_hess_refined))
# percent_change_hessian = np.nan_to_num(percent_change_hessian)


# print percent_change_hessian.mean()



# for i in range(len(percent_change_hessian)):
# 	for j in range(len(percent_change_hessian[0])):
# 		print percent_change_hessian[i][j], "  ", np_hess[i][j], "  ", np_hess_refined[i][j]













# coeff_matrix = [[1+1j, 1j], [2+2j, 3j]]
# ordinate_matrix = [1, 2]

# sol = np.linalg.solve(coeff_matrix, ordinate_matrix)

# print sol

# print np.dot(coeff_matrix, sol)

# sys.exit()




# phonopy_inputs_dictionary = {
# 	'supercell_dimensions': [2, 2, 2],
# 	'symprec': 0.0001,
# 	'displacement_distance': 0.01,
# 	'nac': True
# 	}

# base_path = "C:\Users\Tom\Documents\Berkeley/research\my_papers\Epitaxial Phase Validation Paper\phonon_work/"
# #base_path = "C:\Users/Tom/Documents/Berkeley/courses/ME_C237_Stat_Mech_for_Engineers/final_project/calculation_data/BaTiO3/cubic_2_2_2/"


# init_struct_path = Path.join(base_path, 'initial_structure')
# mod_struct_path = Path.join("C:\Users\Tom\Desktop\Vesta_Inputs\mod.vasp")
# force_constants_path = Path.join(base_path, 'FORCE_CONSTANTS')
# born_path = Path.join(base_path, 'BORN')

# initial_structure = Structure(init_struct_path)


# phonon = phonopy_utility.get_initialized_phononopy_instance(initial_structure, phonopy_inputs_dictionary, force_constants_path, born_path)


# q_points_list = [(0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (0.0, 0.5, 0.0), (0.0, 0.0, 0.5), (0.5, 0.5, 0.0), (0.5, 0.0, 0.5), (0.0, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, 0.5)]

# eig_vecs = phonon.get_frequencies_with_eigenvectors(q_points_list[0])[1]

# #phonopy_utility.view_eigen_values_and_eigen_vectors(phonopy_instance=phonon, q_points_list=q_points_list)


# # qpoint = q_points_list[4]

# # band_index = 2 #1 through 15
# # amplitude = 14.0
# # phase = 0.0

# # band_index -= 1

# # phonon_modes = [[qpoint, band_index, amplitude, phase]]

# # mod_struct = phonopy_utility.get_modulated_structure(phonon, phonopy_inputs_dictionary, phonon_modes)

# # mod_struct.to_poscar_file_path(mod_struct_path)




# pbs = phonopy_utility.get_phonon_band_structure_instance(phonopy_instance=phonon, q_points_list=q_points_list)

# #print pbs


# ps = PhononStructure(primitive_cell_structure=pbs.primitive_cell_structure, phonon_band_structure=pbs, supercell_dimensions_list=phonopy_inputs_dictionary['supercell_dimensions'])


# coordinate_index = 3
# ps.normal_coordinates_list[coordinate_index].coefficient = 1.0

# ps.normal_coordinates_list[111].coefficient = 1.0

# print ps



# ref_struct = ps.reference_supercell_structure

# dist_struct = ps.get_distorted_supercell_structure()

# ref_struct.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs/reference_supercell.vasp")
# dist_struct.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs\distorted.vasp")


# #do the reverse now - go from distorted structure back to normal coordinates.
# ps_new = PhononStructure(primitive_cell_structure=pbs.primitive_cell_structure, phonon_band_structure=pbs, supercell_dimensions_list=phonopy_inputs_dictionary['supercell_dimensions'], 
# 	distorted_structure=dist_struct)

# print ps_new


# dist_struct = ps_new.get_distorted_supercell_structure()

# dist_struct.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs\distorted_2.vasp")




# qpoint = ps.normal_coordinates_list[coordinate_index].normal_mode.q_point_fractional_coordinates


# band_index = ps.normal_coordinates_list[coordinate_index].normal_mode.band_index #1 through 15
# amplitude = ps.normal_coordinates_list[coordinate_index].coefficient*(10.0)
# phase = 0.0

# # band_index -= 1

# print ps.normal_coordinates_list[coordinate_index].normal_mode


# phonon_modes = [[qpoint, band_index, amplitude, phase]]

# mod_struct = phonopy_utility.get_modulated_structure(phonon, phonopy_inputs_dictionary, phonon_modes)

# mod_struct.to_poscar_file_path(mod_struct_path)




# e33_average = 1.0
# e33_spread = 0.2
# min_e33 = e33_average - e33_spread
# max_e33 = e33_average + e33_spread
# e33_distribution_function = lambda x: (e33_spread - (abs(e33_average-x)))**0.4 #very broad bell shape max at 1.0, 0.0 at edges
# e33_distribution = Distribution(e33_distribution_function, min_e33, max_e33)


# e13_average = 0.0
# e13_spread = 0.2
# min_e13 = e13_average - e13_spread
# max_e13 = e13_average + e13_spread
# e13_distribution_function = lambda x: (e13_spread - (abs(e13_average-x)))**0.8 #somewhat broad bell shape max at 0.0, 0.0 at edges
# e13_distribution = Distribution(e13_distribution_function, min_e13, max_e13)


# e23_average = 0.0
# e23_spread = 0.2
# min_e23 = e23_average - e23_spread
# max_e23 = e23_average + e23_spread
# e23_distribution_function = lambda x: (e23_spread - (abs(e23_average-x)))**0.8 #somewhat broad bell shape max at 0.0, 0.0 at edges
# e23_distribution = Distribution(e23_distribution_function, min_e23, max_e23)

# zero_function = lambda : 0.0
# unity_function = lambda : 1.0

# strain_distribution_function_array = [
# 	[unity_function, zero_function, e13_distribution.get_random_value], 
# 	[zero_function, unity_function, e23_distribution.get_random_value], 
# 	[zero_function, zero_function, e33_distribution.get_random_value]
# 	]

# strain_distribution_function_array = [
# 	[1.0, 0.0, e13_distribution], 
# 	[0.0, 1.0, e23_distribution], 
# 	[0.0, 0.0, e33_distribution]
# 	]


# da = DistributionArray(distribution_array=strain_distribution_function_array)
# da.set((0, 0), DistributionGenerator.get_unity_distribution())
# da.set((0, 2), e13_distribution)

# print da.get_random_array()

# dist = Distribution(shape_function=lambda x: x + x**2 + 2.0*x**3.0, min_x=1.0, max_x=10)

# for i in range(10):
# 	print dist.get_random_value()

# print len(dist.cumulative_function)
# print len(dist.inverse_cumulative_function)

# species_list = ['K', 'V', 'O']
# primitive_cell_lattice_constant = 3.79
# supercell_dimensions_list = [4, 4, 1]

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
# 	'species_list': species_list,
# 	'epitaxial_lattice_constant': primitive_cell_lattice_constant*supercell_dimensions_list[0],
# 	'supercell_dimensions_list': supercell_dimensions_list,
# 	'max_number_of_generations': 1,
# 	'individuals_per_generation': [3],
# 	'random_fractions_list': [1.0, 0.3, 0.2],
# 	'mate_fractions_list': [0.0, 0.7, 0.8]
# }

# distribution_function = Distribution(lambda x: 1.0, 0.0, 1.0).get_random_value #uniform
# selection_function = Selector.get_selection_function_for_selecting_N_unique_individuals_by_ranking_using_custom_probability_distribution(distribution_function)

# random_structure_creation_function = StructureGenerator.get_random_perovskite_structure_generator(species_list, primitive_cell_lattice_constant, supercell_dimensions_list)
# structure_mating_function = StructureBreeder.get_perovskite_mating_function(supercell_dimensions_list)

# ga_driver = GADriver(ga_input_dictionary, calculation_set_input_dictionary, selection_function, random_structure_creation_function, structure_mating_function)


# for i in range(0):
# 	struct = ga_driver.get_random_structure(None)
# 	struct.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs\disp_"+str(i)+".vasp")




# struct = ga_driver.structure_mating_function(Structure("C:\Users\Tom\Desktop\Vesta_Inputs\parent_22.vasp"), Structure("C:\Users\Tom\Desktop\Vesta_Inputs\parent_27__.vasp"))
# struct.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs\mated_3.vasp")

# a = 4
# b = 4
# c = 1
# struct_1 = Perovskite(supercell_dimensions = [a, b, c], lattice=[[4.0*a, 0.0, 0.0], [0.0, 4.0*b, 0.0], [0.0, 0.0, 5.0*c]], species_list=['K', 'V', 'O'])

# struct_2 = Structure("C:\Users\Tom\Desktop\Vesta_Inputs\disp_1.vasp")

# sm = SiteMappingCollection(struct_1.sites, struct_2.sites, struct_1.lattice)

# slist = sm.get_interpolated_structure_list(0.1)

# for i,s in enumerate(slist):
# 	s.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs/"+str(i)+".vasp")



# max_x = 10.0

# def func(x, n, max_x):
# 	return 1.0 - ((x**n)/(max_x**n))

# def dist_func(x):
# 	return func(x, 0.1, max_x)

# dist = Distribution(dist_func, 0.0, max_x)

# magnitude_dist_function = dist.get_random_value
# direction_dist_function = Vector.get_random_unit_vector

# vdist = VectorDistribution(direction_dist_function, magnitude_dist_function)

# for i in range(100):
# 	print vdist.get_random_vector()



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
# 	'epitaxial_lattice_constant': 15.16/2.0,
# 	'supercell_dimensions_list': [2, 2, 2],
# 	'max_number_of_generations': 1,
# 	'individuals_per_generation': [3],
# 	'random_fractions_list': [1.0, 0.3, 0.2],
# 	'mate_fractions_list': [0.0, 0.7, 0.8]
# }

# distribution_function = Distribution(lambda x: 1.0, 0.0, 1.0).get_random_value #uniform

# selection_function = Selector.get_selection_function_for_selecting_N_unique_individuals_by_ranking_using_custom_probability_distribution(distribution_function)

# ga_driver = GADriver100PerovskiteEpitaxy(ga_input_dictionary, selection_function, calculation_set_input_dictionary)


# for i in range(10):
# 	struct = ga_driver.get_random_structure(None)
# 	struct.to_poscar_file_path("C:\Users\Tom\Desktop\Vesta_Inputs\disp_"+str(i)+".vasp")


# ga_structure_predictor = GAStructurePredictor(ga_path, ga_driver)

# ga_structure_predictor.update()

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







# class self_c:
# 	def __init__(self):
# 		data_path = ""

# 	def assertEqual(self, left_arg, right_arg = None):
# 		if not right_arg:
# 			print left_arg
# 		else:
# 			print left_arg == right_arg

# 	def assertTrue(self, cond):
# 		print cond

# def get_string(printed):
# 	out_str = '"'
# 	for line in printed:
# 		out_str += line + r'\n'
# 	return out_str + '"'

# self = self_c()

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