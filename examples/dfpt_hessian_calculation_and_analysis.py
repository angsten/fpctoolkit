import sys

from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.io.vasp.outcar import Outcar
from fpctoolkit.phonon.eigen_structure import EigenStructure
from fpctoolkit.structure_prediction.taylor_expansion.variable import Variable
from fpctoolkit.structure_prediction.taylor_expansion.expansion_term import ExpansionTerm
from fpctoolkit.structure_prediction.taylor_expansion.taylor_expansion import TaylorExpansion
from fpctoolkit.structure_prediction.taylor_expansion.derivative_evaluator import DerivativeEvaluator
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation
from fpctoolkit.util.path import Path
from fpctoolkit.phonon.hessian import Hessian
from fpctoolkit.structure.structure import Structure
from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.structure_prediction.taylor_expansion.minima_relaxer import MinimaRelaxer
from fpctoolkit.io.file import File
from fpctoolkit.workflow.epitaxial_relaxer import EpitaxialRelaxer
from fpctoolkit.structure.lattice import Lattice
from fpctoolkit.workflow.vasp_calculation_set import VaspCalculationSet
from fpctoolkit.workflow.vasp_calculation_generator import VaspCalculationGenerator


path = './'

force_calculation_path = Path.join(path, 'dfpt_force_calculation')
relaxed_structure_path = Path.join(path, './2_2_2_supercell_of_relaxed_lda_5_atom_n0p0375_misfit_poscar')

vasp_calculation_input_dictionary = {
    'path': force_calculation_path, #where the vasp_calculation goes
    'structure': relaxed_structure_path, #could also be a path like './poscar', in which case it become the contcar_path for the first run
    'wavecar_path': None, #if not present, no wavecar is used
    'chargecar_path': None, #if not present, not chargecar is used
    'kpoints_scheme': 'Gamma',      #not essential if kspacing in incar is set
    'kpoints_list': '2 2 2',
    'potcar_type': 'lda_paw',       #'lda_paw'  or 'gga_paw_pbe',
    'vasp_code_type': 'standard',   #'standard' or '100' for out-of-plane only relaxation
    'node_count': None,                 #auto-set based on system size and host if not present

    'incar_template': 'static',      #if key not there, just creates a custom incar, can be 'static' or 'external_relaxation'
    'ibrion': 8,
    'lepsilon': True,
    'encut': 400,
    'ediff': 1e-4,
    'lreal': False,     #set based on system size if lreal key is not present,
    'addgrid': True,
    'nsw': 1,
    'npar': 'Remove',

    }

dfpt_force_run = VaspCalculationGenerator(vasp_calculation_input_dictionary)

dfpt_force_run.update()



if not dfpt_force_run.complete:
    sys.exit()

hessian = Hessian(dfpt_force_run.outcar)

if input_dictionary['write_hessian_data']:
    hessian.print_eigenvalues_to_file(Path.join(path, 'output_eigen_values'))
    hessian.print_eigen_components_to_file(Path.join(path, 'output_eigen_components'))
    hessian.print_mode_effective_charge_vectors_to_file(Path.join(path, 'output_mode_effective_charge_vectors'), relaxed_structure)


    eigen_structure = EigenStructure(reference_structure=relaxed_structure, hessian=hessian)

    mode_structures_path = Path.join(path, 'mode_rendered_structures')
    Path.make(mode_structures_path)

    mode_charge_file = File(Path.join(path, 'output_mode_effective_charge_vectors'))

    sorted_eigen_pairs = hessian.get_sorted_hessian_eigen_pairs_list()
    for i, structure in enumerate(eigen_structure.get_mode_distorted_structures_list(amplitude=0.6)):
        if i > 30:
            break
        structure.to_poscar_file_path(Path.join(mode_structures_path, 'u'+str(i+1)+'_'+str(round(sorted_eigen_pairs[i].eigenvalue, 2))+'.vasp'))

        structure.lattice = Lattice([[8.0, 0.0, 0.0], [0.0, 8.0, 0.0], [0.0, 0.0, 8.0]])

        mode_charge_file[i] += '    ' + structure.get_spacegroup_string(symprec=0.2) + '  ' + structure.get_spacegroup_string(symprec=0.1) + '  ' + structure.get_spacegroup_string(symprec=0.001)

        mode_charge_file.write_to_path()
