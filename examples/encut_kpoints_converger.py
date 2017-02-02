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



def encut_converger(base_path, structure, encut_list, base_kpoints_scheme, base_kpoints_subdivisions_list, base_ediff):
    """Takes in a structure, set of encuts, and base params and runs set in base_path""" 
    encut_convergence_set_path = Path.clean(base_path)
    Path.make(encut_convergence_set_path)
    
    for encut in encut_list:
        run_path = Path.join(encut_convergence_set_path, str(encut))
        
        kpoints = Kpoints(scheme_string=base_kpoints_scheme, subdivisions_list=base_kpoints_subdivisions_list)
        incar = IncarMaker.get_static_incar({'ediff':base_ediff, 'encut':encut})
        input_set = VaspInputSet(structure, kpoints, incar)
        
        vasp_run = VaspRun(run_path, input_set=input_set, verbose=False)
        
        if vasp_run.update():
            print encut, round(vasp_run.outcar.energy_per_atom, 5), round(vasp_run.outcar.get_calculation_time_in_core_hours(), 2)
        else:
            pass
            #vasp_run.view(['_job_output.txt'])

def kpoints_converger(base_path, structure, kpoints_lists, base_kpoints_scheme, base_encut, base_ediff, incar_modification_dictionary=None):
    convergence_set_path = Path.clean(base_path)
    Path.make(convergence_set_path)

    for kpoints_list in kpoints_lists:
        run_path = Path.join(convergence_set_path, "_".join(str(kpoints) for kpoints in kpoints_list))

        kpoints = Kpoints(scheme_string=base_kpoints_scheme, subdivisions_list=kpoints_list)
        incar_mod = {'ediff':base_ediff, 'encut':base_encut}
        
        if incar_modification_dictionary:
            for key, value in incar_modification_dictionary.items():
                incar_mod[key] = value
                
        incar = IncarMaker.get_static_incar(incar_mod)
        
        input_set = VaspInputSet(structure, kpoints, incar)

        vasp_run = VaspRun(run_path, input_set=input_set, verbose=False)

        if vasp_run.update():
            print "_".join(str(kpoints) for kpoints in kpoints_list), round(vasp_run.outcar.energy_per_atom, 5), round(vasp_run.outcar.get_calculation_time_in_core_hours(), 2)
        else:
            vasp_run.view(['kpoints','_job_output.txt'])
                

    

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

    #encut convergence*************************************************************************************************
    base_kpoints_scheme = 'Monkhorst'
    base_kpoints_subdivisions_list = [2, 2, 8]
    base_ediff = 0.00000001
        
    encut_list = [100*i for i in range(2,11)]

    Path.make(Path.join('./', 'encut'))

    run_count = 0
    count = 0    
    for name, structure in structure_list.items():
        if count >= run_count:
            break
                    
        print name
        base_path = Path.join('./', 'encut', name)
        Path.make(base_path)
        encut_converger(base_path, structure, encut_list, base_kpoints_scheme, base_kpoints_subdivisions_list, base_ediff)


    #Kpoints convergence ismear 0*************************************************************************************************
    base_kpoints_scheme = 'Monkhorst'
    base_encut = 500 #set this to what we will end up using
    kpoints_lists = [[1, 1, 1], [1, 1, 2], [1, 1, 4], [2, 2, 8], [3, 3, 12]]

    kpoints_path = Path.join('./', 'kpoints_ismear_0')
    Path.make(kpoints_path)

    run_count = 0
    count = 0
    for name, structure in structure_list.items():
        if count >= run_count:
            break
        
        print name
        base_path = Path.join(kpoints_path, name)
        Path.make(base_path)
        kpoints_converger(base_path, structure, kpoints_lists, base_kpoints_scheme, base_encut, base_ediff)
        
        count += 1
    

    #Kpoints convergence ismear -5*************************************************************************************************
    base_kpoints_scheme = 'Gamma'
    base_encut = 500 #set this to what we will end up using
    kpoints_lists = [[1, 1, 1], [1, 1, 2], [1, 1, 4], [2, 2, 8]]
    incar_modification_dictionary = {'ismear':-5,'sigma':0}

    kpoints_path = Path.join('./', 'kpoints_ismear_tetrahedron')
    Path.make(kpoints_path)

    run_count = 1
    count = 0
    for name, structure in structure_list.items():
        if count >= run_count:
            break
        
        print name
        base_path = Path.join(kpoints_path, name)
        Path.make(base_path)
        kpoints_converger(base_path, structure, kpoints_lists, base_kpoints_scheme, base_encut, base_ediff, incar_modification_dictionary)
        
        count += 1
    

    
