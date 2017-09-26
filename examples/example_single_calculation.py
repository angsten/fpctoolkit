from fpctoolkit.workflow.vasp_calculation_set import VaspCalculationSet
from fpctoolkit.workflow.vasp_calculation_generator import VaspCalculationGenerator

vasp_calculation_input_dictionary = {
    'path': './calculation', #where the vasp_calculation goes
    'structure': './poscar', #could also be a path like './poscar', in which case it become the contcar_path for the first run
    'wavecar_path': './wavecar', #if not present, no wavecar is used
    'chargecar_path': './chargecar', #if not present, not chargecar is used
    'kpoints_scheme': 'Gamma',      #not essential if kspacing in incar is set
    'kpoints_list': '6, 6, 4',
    'potcar_type': 'lda_paw',       #'lda_paw'  or 'gga_paw_pbe',
    'vasp_code_type': 'standard',   #'standard' or '100' for out-of-plane only relaxation
    'node_count': 2,                 #auto-set based on system size and host if not present

    'incar_template': 'static',      #if key not there, just creates a custom incar, can be 'static' or 'external_relaxation'
    'encut': 600,
    'ediff': 1e-6,
    'kspacing': 0.5,    #if this is specified, don't need kpoints info below
    'kgamma': True,
    'lreal': False,     #set based on system size if lreal key is not present,
    'npar': 4,          #will be 4 regardless of system size or:
    'npar': None, #npar will not be in incar no matter what or:
    #npar key not present (auto-set based on system size and host)
    #any other incar modifiers
    }

vcalc = VaspCalculationGenerator(vasp_calculation_input_dictionary)

vcalc.update()
