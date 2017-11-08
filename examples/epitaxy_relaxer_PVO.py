#from fpctoolkit.workflow.epitaxial_relaxer import EpitaxialRelaxer

import numpy as np
import copy
import random
from collections import OrderedDict

from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_polarization_run_set import VaspPolarizationRunSet
from fpctoolkit.workflow.epitaxial_relaxer import EpitaxialRelaxer


misfit_strains_list = [-0.04, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06]

path = './'

inputs_dictionaries = {}
relaxation_inputs_dictionaries = {}

inputs_dictionaries['PVO_FM_5_atom'] = {
    'supercell_dimensions_list': [1, 1, 1],
    'misfit_strains_list': misfit_strains_list,
    'reference_lattice_constant': 3.800056,
    'number_of_trials': 5,
    'max_displacement_magnitude': 0.7, #in angstroms
    'max_strain_magnitude': 0.06, #unitless, out-of-plane only when applied
    }

relaxation_inputs_dictionaries['PVO_FM_5_atom'] = {
    'external_relaxation_count': 3, #number of relaxation calculations before static
    'kpoints_scheme': 'Gamma', #or ['Gamma', 'Monkhorst'] #in latter example, would use gamma for first, monkhorst for rest, in first example, gamma for all
    'kpoints_list': '6 6 6',
    'vasp_code_type': '100', #optional, 'standard' (default) or '100'
    'node_count': None, #optional, set by system size if ever None
    'potcar_type': 'gga_paw_pbe', #not needed - defaults to 'lda_paw',
    'ediff': [1e-4, 1e-5, 1e-5],
    'encut': 600,
    'potim': [0.1, 0.2, 0.4],
    'nsw': [41, 111, 191],
    'ispin': 2,
    'magmom': '0.6 1.0 0.6 0.6 0.6',
    'lorbit': 11,
    #'isif' : [5, 2, 3],
    #any other incar parameters with value as a list
    }



epitaxial_relax = EpitaxialRelaxer(path=path, inputs_dictionaries=inputs_dictionaries, relaxation_inputs_dictionaries=relaxation_inputs_dictionaries, calculate_polarizations=False)
epitaxial_relax.update()

print epitaxial_relax.data_dictionaries

print '\n\n'
low_en_dd = epitaxial_relax.get_lowest_energy_data_dictionaries()


print "full data dict"
for structure_tag in epitaxial_relax.data_dictionaries:
    print structure_tag

    ordered_misfits = sorted(epitaxial_relax.data_dictionaries[structure_tag])

    for misfit in ordered_misfits:
        print "Misfit strain: " + str(misfit)

        for trial in epitaxial_relax.data_dictionaries[structure_tag][misfit]:
            print trial


print '\nMinimum energy dicts'
for structure_tag in low_en_dd:
    print structure_tag

    ordered_misfits = sorted(low_en_dd[structure_tag])

    for misfit in ordered_misfits:
        print "Misfit strain: " + str(misfit)

        print low_en_dd[structure_tag][misfit]


print '\n\n\n'
epitaxial_relax.print_lowest_energies()

#print "Status of epitaxial relaxations: Complete: " + str(epitaxial_relax.complete)
