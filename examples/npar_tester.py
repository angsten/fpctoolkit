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
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.io.vasp.incar_maker import IncarMaker



def npar_converger(base_path, structure, npar_list, base_kpoints_scheme, base_kpoints_subdivisions_list, base_ediff, base_encut, node_count):
    """Takes in a structure, set of npars, and base params and runs set in base_path"""
    encut_convergence_set_path = Path.clean(base_path)
    Path.make(encut_convergence_set_path)

    for npar in npar_list:
        run_path = Path.join(encut_convergence_set_path, str(npar))

        input_dictionary = {
            'external_relaxation_count': 0,
            'kpoint_schemes_list': [base_kpoints_scheme],
            'kpoint_subdivisions_lists': [base_kpoints_subdivisions_list],
            'submission_script_modification_keys_list': ['100'],
            'submission_node_count_list': [node_count],
            'ediff': [base_ediff],
            'encut': [base_encut],
            'npar': [npar]
            }


        vasp_relaxation = VaspRelaxation(run_path, structure, input_dictionary, verbose=False)

        if vasp_relaxation.update():
            print "npar:", npar, "node_count:", node_count, round(vasp_relaxation.get_final_energy(True),5), round(vasp_relaxation.total_time, 2)
        else:
            pass

def get_structure_list(path):
    """loads in poscars at path and returns list of structures"""

    path = Path.clean(path)
    files = Path.get_list_of_files_at_path(path)
    structs = {}

    for file in files:
        structs[file] = Structure(Path.join(path, file))

    return structs

if __name__ == "__main__":
    print (150*"*"+'\n')*3

    structure_list = get_structure_list('./structures')

    #npar convergence*************************************************************************************************
    base_kpoints_scheme = 'Monkhorst'
    base_kpoints_subdivisions_list = [1, 1, 4]
    base_ediff = 0.001
    base_encut = 500

    npar_list = [1, 2, 4, 8, 16]

    base_path_outer = Path.join('./', 'npar')
    Path.make(base_path_outer)

    run_count = 1

    for node_count in range(1,5):
        base_path_inner = Path.join(base_path_outer, "node_count_is_" + str(node_count))
        Path.make(base_path_inner)

        count = 0
        for name, structure in structure_list.items():
            if count >= run_count:
                break

            print name
            base_path = Path.join(base_path_inner, name)
            Path.make(base_path)
            npar_converger(base_path, structure, npar_list, base_kpoints_scheme, base_kpoints_subdivisions_list, base_ediff, base_encut, node_count)

            count += 1
