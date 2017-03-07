"""
This program takes a perovskite structure of a given composition and searches for the global minimum
in the energy under given (100) epitaxial constraints (a and b lattice vectors equal in magnitude, normal, 
and fixed). The search is performed around the perfect cubic perovskite structure, and the A lattice is 
mostly preserved in this search as a roughly square lattice (if this were not so, the structure would not
persist without extremely high interfacial energies as an epitaxial film).
"""

from fpctoolkit.structure_prediction.ga_structure_predictor import GAStructurePredictor
from fpctoolkit.structure_prediction.ga_driver_100_perovskite_epitaxy import GADriver100PerovskiteEpitaxy



Nx = 4
Nz = 1

ga_path = "./" + str(Nx) + 'x' + str(Nx) + 'x1'

calculation_set_input_dictionary = {
    'external_relaxation_count': 6,
    'kpoint_schemes_list': ['Monkhorst'],
    'kpoint_subdivisions_lists': [[1, 1, 4]],
    'submission_script_modification_keys_list': ['100'],
    'submission_node_count_list': [2],
    'ediff': [0.001, 0.001, 0.001, 0.0001, 0.0001, 0.0001],
    'potim': [0.01,  0.05,  0.2,   0.1,    0.4],
    'nsw':   [41,    81,    161,   41,     81,     161],
    'encut': [500]
    }

ga_input_dictionary = {
    'species_list':['K','V', 'O'],
    'epitaxial_lattice_constant': 15.16,
    'supercell_dimensions_list': [Nx, Nx, Nz],
    'max_number_of_generations': 5,
    'individuals_per_generation': [40],
    'random_fractions_list': [1.0, 0.4],
    'mate_fractions_list': [0.0, 0.6]
    }

ga_driver = GADriver100PerovskiteEpitaxy(ga_input_dictionary, calculation_set_input_dictionary)

ga_structure_predictor = GAStructurePredictor(ga_path, ga_driver)

ga_structure_predictor.update()

#print "Total population looks like\n\n\n\n"
#print ga_structure_predictor.get_total_population()




