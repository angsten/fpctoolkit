import sys

from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.util.path import Path
from fpctoolkit.structure.displacement_vector import DisplacementVector
from fpctoolkit.phonon.hessian import Hessian
from fpctoolkit.phonon.eigen_structure import EigenStructure
from fpctoolkit.io.vasp.outcar import Outcar




a = 3.79
Nx = 1
Ny = 1
Nz = 1

relax_input_dictionary = {
	'external_relaxation_count': 3,
	'kpoint_schemes_list': ['Monkhorst'],
	'kpoint_subdivisions_lists': [[6, 6, 6]],
	'submission_node_count_list': [1],
	'ediff': [1e-5, 1e-6, 1e-7],
	'potim': [0.05, 0.1, 0.3],
	'encut': [800]
	}

supercell_dimensions = [Nx, Ny, Nz]
base_path = './'

outcar = Outcar(Path.join(base_path, 'OUTCAR_small_refined'))
hessian = Hessian(outcar)

reference_structure=Perovskite(supercell_dimensions=[Nx, Ny, Nz], lattice=[[a*Nx, 0.0, 0.0], [0.0, a*Ny, 0.0], [0.0, 0.0, a*Nz]], species_list=['Sr', 'Ti', 'O'])

# print eigen_structure
# print eigen_structure.eigen_components_list[component_index]
# eigen_structure.print_eigen_components()


random_chromosomes = [[0.0, 0.0, 0.05, 0.02, -0.01, 0.0,    0.0, 0.0, 0.0,  0.2, 0.15, -0.08, 0.2, 0.1],
					  [0.0, 0.0, -0.1, 0.2, 0.0, 0.0,       0.0, 0.0, 0.0,  0.5, 0.65, -0.8, 0.1, 0.0, 0.0, 0.0, 0.6, 0.0, -0.8],
					  [0.0, 0.0, 0.02, 0.02, 0.02, 0.0,     0.0, 0.0, 0.0,  0.0, 0.0, 0.0, 0.0, 0.02, 0.06, 0.1, 0.3, 0.5, -0.6, 0.3, 0.2]]



for chromosome_index, chromosome in enumerate(random_chromosomes):
	eigen_structure = EigenStructure(reference_structure=reference_structure, hessian=hessian)

	relaxation_path = Path.join(base_path, "chromosome_index_" + str(chromosome_index))
		
	Path.make(relaxation_path)


	eigen_structure.set_eigen_chromosome(chromosome)


	print "Chromosome index is " + str(chromosome_index) + "\n\t initial eigenstructure is " + str(eigen_structure)

	distorted_structure = eigen_structure.get_distorted_structure()


	relax = VaspRelaxation(path=relaxation_path, initial_structure=distorted_structure, input_dictionary=relax_input_dictionary)

	relax.update()


	if relax.complete:
		relaxed_structure = relax.final_structure
		relaxed_eigen_structure = EigenStructure(reference_structure=reference_structure, hessian=hessian, distorted_structure=relaxed_structure)
		print "\t   final eigenstructure is " + str(relaxed_eigen_structure) + " " + str(relax.get_final_energy())