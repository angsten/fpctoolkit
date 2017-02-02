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


if __name__ == "__main__":

    path = './relaxation_BTO_2'
    initial_structure = Perovskite(supercell_dimensions=[1, 1, 1], lattice=[[4.1, 0.1, 0.0], [0.0, 4.0, 0.0], [0.0, 0.1, 3.9]], species_list=['Ba', 'Ti', 'O'])
    input_dictionary = {
        'external_relaxation_count': 2,
        'kpoint_schemes_list': ['Monkhorst'],
        'kpoint_subdivisions_lists': [[2, 2, 2], [4, 4, 4], [6, 6, 6]],
        'ediff': [0.001, 0.0001, 0.00001],
        'encut': [400, 600]
    }


    relax = VaspRelaxation(path, initial_structure, input_dictionary)
    relax.update()
    relax.view(['poscar','contcar'])
