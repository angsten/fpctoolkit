from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_calculation_generator import VaspCalculationGenerator
from fpctoolkit.workflow.vasp_calculation_set import VaspCalculationSet
from fpctoolkit.workflow.vasp_calculation_set_generator import VaspCalculationSetGenerator
from fpctoolkit.workflow.convenient_vasp_calculation_set_generator import ConvenientVaspCalculationSetGenerator

import copy

base_path = './'

external_relaxations = 0

paths = [Path.join(base_path, 'relax_' + str(i)) for i in range(1, external_relaxations+1)] + [Path.join(base_path, 'static')] + [Path.join(base_path, x) for x in ['dos_static_from_chargcar']]

vasp_calculation_set_input_dictionary = {
    'path': paths,
    'structure': ['./PVO_expermental_5_atom_structure'] + ['use_last']*external_relaxations + ['use_last']*1,
    'wavecar_path': [None] + ['use_last']*external_relaxations + [None],
    'chargecar_path': [None] + ['use_last']*external_relaxations + ['use_last'],
    'kpoints_scheme': 'Gamma',
    'kpoints_list': ['6 6 6']*(external_relaxations+1) + ['10 10 10'],
    'potcar_type': 'gga_paw_pbe',
    'vasp_code_type': 'standard',
    'node_count': None,
    'incar_template': ['external_relaxation']*external_relaxations + ['static']*2,
    'encut': 400,
    'ediff': 1e-4,
    #'kspacing': 0.3,
    #'kgamma': True,
    'ismear': -5,
    #'precfock': [None]*external_relaxations + [None, 'Fast', 'Fast', 'Fast'],
    #'nkred': [None]*external_relaxations + [None, 2, 2, 2],
    #'algo': [None]*external_relaxations + [None, 'All', None, None],
    #'ialgo': [None]*external_relaxations + [None, None, 53, 53],
    #'time': [None]*external_relaxations + [None, 0.4, 0.4, 0.4],
    'icharg': [None]*external_relaxations + [None, 11],
    'lorbit': 11,
    'ispin': 2,
    'magmom': '0.6 1.0 0.6 0.6 0.6',
    'nedos': 4001,
    #'lhfcalc': [None]*external_relaxations + [None, True, True, True],
    #'hfscreen': [None]*external_relaxations + [None, 0.2, 0.2, 0.2]
    #'lreal': False,     #set based on system size if lreal key is not present,
    #'npar': 4,          #will be 4 regardless of system size or:
    #'npar': None, #npar will not be in incar no matter what or:
    #npar key not present (auto-set based on system size and host)
    #any other incar modifiers
    }




vcalc_set = ConvenientVaspCalculationSetGenerator(vasp_calculation_set_input_dictionary=vasp_calculation_set_input_dictionary)

vcalc_set.update()
