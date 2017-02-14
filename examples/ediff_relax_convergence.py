from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.potcar import Potcar
from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.io.vasp.incar import Incar
from fpctoolkit.util.path import Path
from fpctoolkit.io.file import File
from fpctoolkit.structure.site import Site
from fpctoolkit.structure.lattice import Lattice
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.structure.site_collection import SiteCollection
from fpctoolkit.io.vasp.outcar import Outcar
from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation

import os
import sys

def get_random_structure():
    a = 15.16
    structure = Perovskite(supercell_dimensions = [4, 4, 1], lattice=[[a, 0.0, 0.0], [0.0, a, 0.0], [0.0, 0.0, a/4.0]], species_list=['K', 'V', 'O'])

    shear_factor = 1.0
    structure.lattice.randomly_strain(stdev=0.08, mask_array=[[0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 2.0*shear_factor], [0.0, 0.0, 1.0]]) #for (100) epitaxy

    mult = 2.4#1.8
    min_atomic_distance = 1.5
    print structure.randomly_displace_site_positions(stdev=0.2*mult, enforced_minimum_atomic_distance=min_atomic_distance, max_displacement_distance=0.3*mult, mean=0.3, types_list=['K'])
    print structure.randomly_displace_site_positions(stdev=0.6*mult, enforced_minimum_atomic_distance=min_atomic_distance, max_displacement_distance=0.6*mult, mean=0.5, types_list=['V'])
    print structure.randomly_displace_site_positions(stdev=0.8*mult, enforced_minimum_atomic_distance=min_atomic_distance, max_displacement_distance=1.2*mult, mean=0.7, types_list=['O'])

    return structure

if __name__ == "__main__":

    print "\n"*50

    '''
    Path.make("./structures_3")

    for i in range(5):
        structure = get_random_structure()
        structure.to_poscar_file_path("./structures_3/random_structure_" + str(i))

    sys.exit()
    '''

    relaxes = []
    potims = [0.05, 0.2, 0.5, 1.0]

    for k in range(len(potims)):
        struct_range = 5
        for i in range(struct_range):
            structure = Structure('./structures_3/random_structure_' + str(i))
            potim = potims[k]
            path = './relaxation_type_potim_equals_'+str(potim).replace('.','o')+'_trial_' + str(i)
            input_dictionary = {
                'external_relaxation_count': 4,
                'kpoint_schemes_list': ['Monkhorst'],
                'kpoint_subdivisions_lists': [[1, 1, 4]],
                'submission_script_modification_keys_list': ['100'],
                'submission_node_count_list': [2],
                'ediff': [0.001, 0.001, 0.0001, 0.0001],
                'encut': [500],
                'potim': [potim]
            }

            relaxes.append(VaspRelaxation(path, structure, input_dictionary, verbose=False))

    for relax in relaxes:
        relax.update()
        print os.path.basename(relax.path)
        if not relax.complete:
            #relax.view(['_job_output.txt'])
            relax.quick_view()

    for relax in relaxes:
        print os.path.basename(relax.path)

        #print relax.get_final_energy(), relax.total_time
        data_dict = relax.get_data_dictionary()

        for i in range(len(data_dict['run_final_energy_per_atom_list'])):
            if data_dict['run_final_energy_per_atom_list'][i]:
                print round(data_dict['run_final_energy_per_atom_list'][i],6), data_dict['run_total_time_list'][i]


        #print " ".join(str(round(val, 5)) for val in data_dict['run_final_energy_per_atom_list'])
        #print " ".join(str(time) for time in data_dict['run_total_time_list'])
