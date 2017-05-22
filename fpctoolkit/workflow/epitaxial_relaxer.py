#from fpctoolkit.workflow.epitaxial_relaxer import EpitaxialRelaxer

import numpy as np
import copy

from fpctoolkit.util.path import Path
from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.workflow.vasp_run_set import VaspRunSet
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet
from fpctoolkit.structure.structure import Structure
from fpctoolkit.io.file import File
import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.workflow.vasp_relaxation import VaspRelaxation

class EpitaxialRelaxer(object):
	"""
	Calculates the minimum energy structures across a series of (100) misfit strains.
	"""

	def __init__(self, path, initial_structures_list, vasp_relaxation_inputs_dictionary, reference_lattice_constant, misfit_strains_list):
		"""
		path should be the main path of the calculation set

		initial_structures_list should be the set of structures that are relaxed at each misfit strain

		vasp_relaxation_inputs_dictionary should look something like:
		{
			'external_relaxation_count': 4,
			'kpoint_schemes_list': ['Gamma'],
			'kpoint_subdivisions_lists': [[1, 1, 1], [1, 1, 2], [2, 2, 4]],
			'submission_script_modification_keys_list': ['100', 'standard', 'standard_gamma'], #optional - will default to whatever queue adapter gives
			'submission_node_count_list': [1, 2],
			'ediff': [0.001, 0.00001, 0.0000001],
			'encut': [200, 400, 600, 800],
			'isif' : [5, 2, 3]
			#any other incar parameters with value as a list
		}

		reference_lattice_constant should be the lattice constant a0 which, when multiplied by the list of misfit strains, generates the new in-plane lattice constant at those strains.

		For each lattice constant and each structure, a relaxation is performed. Then, the lowest energy structures at each misfit strain can be determined, and a convex hull results.
		"""

		for structure in initial_structures_list:
			Structure.validate(structure)

		basic_validators.validate_real_number(reference_lattice_constant)

		for misfit_strain in misfit_strains_list:
			basic_validators.validate_real_number(misfit_strain)


		self.path = path
		self.initial_structures_list = initial_structures_list
		self.vasp_relaxation_inputs_dictionary = vasp_relaxation_inputs_dictionary
		self.reference_lattice_constant = reference_lattice_constant
		self.misfit_strains_list = misfit_strains_list

		Path.make(path)

		self.initialize_vasp_relaxations()
		self.update()


	def initialize_vasp_relaxations(self):
		"""
		"""

		self.vasp_relaxations_list = []

		for misfit_strain in self.misfit_strains_list:
			lattice_constant = self.reference_lattice_constant*(1.0+misfit_strain)

			for i, initial_structure in enumerate(self.initial_structures_list):
				structure = copy.deepcopy(initial_structure)

				if abs(structure.lattice[0][1]) > 0.0 or abs(structure.lattice[0][2]) > 0.0 or abs(structure.lattice[1][0]) > 0.0 or abs(structure.lattice[1][2]) > 0.0:
					raise Exception("Current lattice is incompatible with (100) epitaxy: ", str(structure.lattice))

				structure.lattice[0][0] = lattice_constant
				structure.lattice[1][1] = lattice_constant

				#break symmetry
				structure.randomly_displace_sites(max_displacement_magnitude=0.01)


				relax_path = Path.join(self.path, str(misfit_strain), 'structure_' + str(i))

				relaxation = VaspRelaxation(path=relax_path, initial_structure=structure, input_dictionary=self.vasp_relaxation_inputs_dictionary)

				self.vasp_relaxations_list.append(relaxation)




	def update(self):

		for relaxation in self.vasp_relaxations_list:
			relaxation.update()

	@property
	def complete(self):
		for relaxation in self.vasp_relaxations_list:
			if not relaxation.complete:
				return False

		return True