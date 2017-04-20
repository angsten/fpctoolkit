#from fpctoolkit.phonon.phonon_super_displacement_vector import PhononSuperDisplacementVector

import numpy as np
from collections import OrderedDict
import cmath

import fpctoolkit.util.basic_validators as basic_validators
from fpctoolkit.structure.displacement_vector import DisplacementVector


class PhononSuperDisplacementVector(object):
	"""
	Represents a supercell displacement vector generated from a phonon normal mode. This vector has an x, y, and z 
	component of displacement for each atom in the supercell. It is thus of length 3*Nat*Ncell.

	This class is the vec(U)sup(y,j)sub(lambda) in the math notation. It is associated with a normal mode with q_point y and
	band index j. Lambda controls whether or not this is the displacement for a real (lambda = 1) or imaginary normal mode component (lambda = 2).
	"""

	def __init__(self, normal_mode_instance, lambda_index, reference_supercell, supercell_dimensions_list):
		"""
		"""

		if lambda_index not in [1, 2]:
			raise Exception("Lambda index must either be one (for real complex normal coordinate component) or two (for imaginary):", lambda_index)


		self.normal_mode = normal_mode_instance
		self.displacement_vector = DisplacementVector(reference_supercell, coordinate_mode="Cartesian")
		self.lambda_index = lambda_index
		self.reference_supercell = reference_supercell
		self.supercell_dimensions_list = supercell_dimensions_list
		self.cell_count = supercell_dimensions_list[0]*supercell_dimensions_list[1]*supercell_dimensions_list[2]

		self.set_displacements()

	def __str__(self):
		return "q=" + str(self.normal_mode.q_point_fractional_coordinates) + ", band=" + str(self.normal_mode.band_index+1) + ", lambda=" + str(self.lambda_index) + "\ndisplacement vector: " + str(self.displacement_vector)

	def set_displacements(self):
		"""
		Set the components of self.displacement_vector by applying e(k y/j)*exp(2*pi*ydotx(l/k)) for each atom k and cell l.
		Displacements are use a Cartesian mode with Angstroms as the units (or whatever units the eigen_displacements_vector uses).
		"""

		q_vector = self.normal_mode.q_point_fractional_coordinates
		eigen_displacements_vector = self.normal_mode.eigen_displacements_list
		cell_count = self.supercell_dimensions_list[0]*self.supercell_dimensions_list[1]*self.supercell_dimensions_list[2]

		self.reference_supercell.convert_sites_to_direct_coordinates()


		for i, site in enumerate(self.reference_supercell.sites):

			#index to site number in the primitive cell - can range from 0 to Nat-1, where there are Nat in the primitive cell
			#this serves as an index to the eigen_displacements_vector
			atom_index = int(i/(cell_count))

			#this marks the cell the site is in - for instance, 1, 1, 1 in a 2x2x2 supercell means the atom is in the center of the supercell
			#this is x(l/k) in the formula
			site_supercell_position = [site['position'][i]*self.supercell_dimensions_list[i] for i in range(3)] 


			#e(k|y/j)*exp(2*pi*i*ydotx(l/k)) --> defaults to Angstroms in Cartesian system
			atomic_displacement = eigen_displacements_vector[3*atom_index:3*atom_index+3]*cmath.exp(2.0*cmath.pi*1.0j*np.dot(q_vector, site_supercell_position))

			for j in range(3):
				if self.lambda_index == 1:
					self.displacement_vector[i*3+j] = atomic_displacement[j].real
				elif self.lambda_index == 2:
					self.displacement_vector[i*3+j] = -1.0*atomic_displacement[j].imag




