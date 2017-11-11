from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_relaxation_calculation import VaspRelaxationCalculation
from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.structure.structure import Structure
from fpctoolkit.io.file import File
from fpctoolkit.structure.displacement_vector import DisplacementVector
from fpctoolkit.io.vasp.outcar import Outcar

import sys
import copy
import time
import pickle
import os


def get_sample(calculation_path):
    structure = Structure(file_path=Path.join(calculation_path, 'POSCAR'))
    structure.shift_sites_so_first_atom_is_at_origin()

    outcar = Outcar(file_path=Path.join(calculation_path, 'OUTCAR'))

    lattice_information = structure.get_magnitudes_and_angles()

    ideal_perovskite_structure = Perovskite(supercell_dimensions=[1, 1, 1], lattice=copy.deepcopy(structure.lattice), species_list=structure.get_species_list())

    displacement_vector = DisplacementVector.get_instance_from_displaced_structure_relative_to_reference_structure(reference_structure=ideal_perovskite_structure, displaced_structure=structure, coordinate_mode='Cartesian')

    energy = outcar.energy

    forces = outcar.final_forces_list

    stresses = outcar.final_stresses_list
    volume = structure.lattice.get_volume() #in A^3

    for z in range(len(stresses)):
        stresses[z] /= volume

    row_of_data = lattice_information + displacement_vector.to_list() + [energy] + forces + stresses

    output_string = ' '.join([str(x) for x in row_of_data])

    return row_of_data, output_string



i = 0
for path in os.listdir('./'):
    if os.path.isdir(path):
        run_path = Path.join(path, 'static')

        species_list = Structure(file_path=Path.join(run_path, 'POSCAR')).get_species_list()
        species_string = ''.join([str(x) for x in species_list]) + '3'

        print species_string + ' ' + str(i),
        print get_sample(run_path)[1]
        i += 1
