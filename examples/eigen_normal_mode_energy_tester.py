import fpctoolkit.util.phonopy_interface.phonopy_utility as phonopy_utility

from fpctoolkit.workflow.vasp_phonon import VaspPhonon

from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.util.path import Path
from fpctoolkit.structure.displacement_vector import DisplacementVector
from fpctoolkit.phonon.hessian import Hessian
from fpctoolkit.phonon.eigen_structure import EigenStructure




a = 3.79
Nx = 1
Ny = 1
Nz = 1

relax_input_dictionary = {
	'external_relaxation_count': 0,
	'kpoint_schemes_list': ['Monkhorst'],
	'kpoint_subdivisions_lists': [[6, 6, 6]],
	'submission_node_count_list': [1],
	'ediff': [0.000001],
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


component_indices = range(len(eigen_structure.eigen_components_list))


for component_index in component_indices:
	eigen_structure = EigenStructure(reference_structure=reference_structure, hessian=hessian)

	component_path = Path.join(base_path, "component_index_" + str(component_index))
		
	Path.make(component_path)

	print "Component index is " + str(component_index) + ", eigenvalue is " + str(eigen_structure[component_index+6])

	for i in range(3):
		relaxation_path = Path.join(component_path, str(i))
		
		eigen_structure[component_index+6] = i*0.05

		distorted_structure = eigen_structure.get_distorted_structure()


		relax = VaspRelaxation(path=relaxation_path, initial_structure=distorted_structure, input_dictionary=relax_input_dictionary)

		relax.update()


		if relax.complete:
			relaxed_structure = relax.final_structure

			print str(eigen_structure[component_index+6]), relax.get_final_energy()