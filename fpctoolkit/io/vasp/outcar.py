import numpy as np

from fpctoolkit.io.file import File
import fpctoolkit.util.string_util as su

class Outcar(File):
	
	run_complete_string = "Total CPU time used (sec):"
	ionic_step_complete_string = "aborting loop because EDIFF is reached"
	total_energy_string = "energy(sigma->0)"
	dielectric_tensor_string = "MACROSCOPIC STATIC DIELECTRIC TENSOR (including local field effects in DFT)"
	born_effective_charge_tensor_string = "BORN EFFECTIVE CHARGES (in e, cummulative output)"
	hessian_string = "SECOND DERIVATIVES (NOT SYMMETRIZED)"
	forces_string = "POSITION                                       TOTAL-FORCE (eV/Angst)"

	def __init__(self, file_path=None):
		super(Outcar, self).__init__(file_path)


	def reload(self):
		"""Reloads from original file_path to refresh lines"""

		super(Outcar, self).__init__()		


	@property
	def complete(self):
		"""Searches the last few lines for the tag 'Total CPU time used (sec):'
		If this tag is present, returns True. Reverse traversing is done for
		efficiency.
		"""

		return bool(self.get_first_line_containing_string_from_bottom(Outcar.run_complete_string, stop_after=200))

	@property
	def energy(self):
		if not self.complete:
			raise Exception("Run does not have a final energy yet - not completed.")

		total_energy_line = self.get_first_line_containing_string_from_bottom(Outcar.total_energy_string)
		return float(total_energy_line.split('=')[-1].strip())


	@property
	def energy_per_atom(self):
		return self.energy / self.get_number_of_atoms()

	@property
	def final_forces_list(self):
		"""
		Returns list of forces - one for each x, y, z component of each atom, ordered by poscar position.
		"""

		if not self.complete:
			raise Exception("Run not yet completed - cannot get forces list")

		forces_start_indices = self.get_line_indices_containing_string(Outcar.forces_string)

		if len(forces_start_indices) == 0:
			raise Exception("No set of forces found in completed outcar file")

		forces_start_index = forces_start_indices[-1] + 2

		final_forces_list = []

		for line_index in range(self.get_number_of_atoms()):
			line = self.lines[forces_start_index + line_index]
				
			row_number_list = su.get_number_list_from_string(line)

			if not len(row_number_list) == 6:
				raise Exception("Error reading row from forces data. Length should be 6 but is not. Row number list looks like", row_number_list)

			final_forces_list += row_number_list[3:6]		


		if len(final_forces_list) != self.get_number_of_atoms()*3:
			raise Exception("Incorrect number of forces obtained:", final_forces_list)

		return final_forces_list


	def get_ionic_energies(self):
		"""Returns list of energies (one for each ionic step) currently present in outcar"""

		ionic_step_data_start_line_indices = self.get_line_indices_containing_string(Outcar.ionic_step_complete_string)
		print ionic_step_data_start_line_indices
		##########unfinished

	def get_number_of_atoms(self):
		return self.get_incar_parameter_value("NIONS")


	def get_calculation_time_in_core_hours(self):
		"""In cpu*hours. Good for comparing speed up when moving from smaller to larger number of cores"""

		total_cpu_time = self.get_total_cpu_time()
		number_of_cores = self.get_number_of_cores()

		if (not total_cpu_time) or (not number_of_cores):
			return None
			
		cpu_hours = (total_cpu_time * number_of_cores) / 3600.0
		
		return round(cpu_hours, 2)

	def get_number_of_cores(self):
		"""Returns number of cores recorded in outcar"""

		core_count_line = self.get_first_line_containing_string_from_top("total cores") #may be fenrir specific!

		if not core_count_line:
			return None

		core_count_line = su.remove_extra_spaces(core_count_line)

		return int(core_count_line.split(' ')[2])

	def get_total_cpu_time(self):
		"""Returns number after Total CPU time used (sec): string"""

		cpu_time_line = self.get_first_line_containing_string_from_bottom("Total CPU time used (sec):")

		if not cpu_time_line:
			return None

		cpu_time_line = su.remove_extra_spaces(cpu_time_line).strip()

		return float(cpu_time_line.split(' ')[5])


	def get_incar_parameter_value(self, key):
		"""
		Key is some parameter that will be found in the outcar, such as NIONS or ISIF.
		Returns the value as string or numerical value if possible. Returns none if nothing
		found in outcar. Looks for first thing with spaces around it after the key name.
		"""

		containing_lines = self.get_lines_containing_string(key)

		if len(containing_lines) == 0:
			return None

		line = containing_lines[0]
		line = su.remove_extra_spaces(line).strip() #'bla bla NIONS = 40 bla bla bla'
		line = line.split(key)[1].strip() #get everything after key '= 40 bla bla bla'
		value = line.split(" ")[1]

		if su.string_represents_integer(value):
			return int(value)
		elif su.string_represents_float(value):
			return float(value)
		else:
			return value



	def get_dielectric_tensor(self):
		"""
		Returns a 3x3 dielectric tensor with component (0, 0) as eps_xx and so forth.
		"""

		if not self.complete:
			raise Exception("Run does not yet have a dielectric tensor - not completed")

		tensor_start_indices = self.get_line_indices_containing_string(Outcar.dielectric_tensor_string)

		if len(tensor_start_indices) == 0:
			raise Exception("No dielectric tensor found in completed outcar file")

		tensor_start_index = tensor_start_indices[-1] + 2

		dielectric_tensor = []

		for line in self.lines[tensor_start_index:tensor_start_index+3]:
			row_number_list = su.get_number_list_from_string(line)

			if not len(row_number_list) == 3:
				raise Exception("Error reading row from dielectric tensor. Length should be 3 but is not. Row number list looks like", row_number_list)

			dielectric_tensor.append(row_number_list)

		return dielectric_tensor


	def get_born_effective_charge_tensor(self):
		"""
		Returns an Nx3x3 tensor, where N is the number of atoms in the POSCAR of the calculation. The Born Effective Charge Tensor looks like:

		BORN EFFECTIVE CHARGES (in e, cummulative output)
		 -------------------------------------------------
		 ion    1
		    1     2.55248     0.00000     0.00001
		    2     0.00000     2.55247     0.00000
		    3     0.00001     0.00000     2.59358   <---- this last component is indexed by [0][2][2] and represents the change in the z-component of polarization with z-displacement of atom 1
		 ion    2
		    1     7.24494     0.00000     0.00009
		    2     0.00000     7.24494     0.00001
		    3     0.00010     0.00001     6.01323
		 ion    3
		    1    -5.77788     0.00000    -0.00004
		    2     0.00000    -2.00260     0.00000
		    3    -0.00009     0.00000    -1.89826
		    				.
		    				.
		    				.
		ion     N

		"""

		if not self.complete:
			raise Exception("Run does not yet have a born effective charge tensor - not completed")

		tensor_start_indices = self.get_line_indices_containing_string(Outcar.born_effective_charge_tensor_string)

		if len(tensor_start_indices) == 0:
			raise Exception("No born effective charge tensor found in completed outcar file")

		tensor_start_index = tensor_start_indices[-1] -1

		born_effective_charge_tensor = []

		for N in range(self.get_number_of_atoms()):
			atomic_tensor = []

			tensor_start_index += 4

			for line in self.lines[tensor_start_index:tensor_start_index+3]:
				row_number_list = su.get_number_list_from_string(line)[1:]

				if not len(row_number_list) == 3:
					raise Exception("Error reading row from born effect charge tensor. Length should be 3 but is not. Row number list looks like", row_number_list)
					
				atomic_tensor.append(row_number_list)

			born_effective_charge_tensor.append(atomic_tensor)			

		return born_effective_charge_tensor

	
	def get_hessian_matrix(self):
		"""
		Returns an NxN matrix of second derivatives w.r.t. atomic displacements (force constant units are eV/Angstrom^2 in matrix), where N is the number of atoms in the POSCAR of the calculation. 

		The matrix of second derivatives is arranged as:
			         atom_1_x     atom_1_y   atom_1_z  atom_2_x ... atom_N_z
		atom_1_x      -8.4           0.0       0.0       3.2           6.5
		atom_1_y      -1.02          ...
		atom_1_z
		atom_2_x
		.
		.
		.
		atom_N_z

		The output is a list of lists, looking like [[d^2E/du_atom_1_x*du_atom_1_x, d^2/du_atom_1_x*du_atom_1_y, ...], [d^2/du_atom_1_y*du_atom_1_x, ...], ...]

		Here, atom_n is the nth atom in the poscar file.

		NOTE: The negative of the components of the OUTCAR is taken because vasp puts derivatives in terms of forces, which are -dE/dx.
		"""

		hessian_matrix = []

		hessian_matrix_indices = self.get_line_indices_containing_string(Outcar.hessian_string)

		if len(hessian_matrix_indices) == 0:
			raise Exception("No hessian matrix found in completed outcar file")


		hessian_matrix_starting_index = hessian_matrix_indices[-1] + 3


		number_of_degrees_of_freedom = 3*self.get_number_of_atoms()

		for i in range(number_of_degrees_of_freedom):
			row_string = self[hessian_matrix_starting_index+i]

			cleaned_row_string = su.remove_extra_spaces(row_string.strip())

			cleaned_row_components_list = cleaned_row_string.strip().split(' ')

			numerical_strings_list = cleaned_row_components_list[1:]

			row_values_list = [-1.0*float(component_string) for component_string in numerical_strings_list] #must take the negative because vasp gives values in terms of changes in forces, which are negative of dEnergy terms

			if not len(row_values_list) == number_of_degrees_of_freedom:
				raise Exception("Number of degrees of freedom and number of columns in hessian row do not match. Row is", row_values_list, "number of dofs is", number_of_degrees_of_freedom)


			hessian_matrix.append(row_values_list)

		if len(hessian_matrix) != number_of_degrees_of_freedom:
			raise Exception("Number of degrees of freedom and number of rows in hessian matrix do not match. Matrix row count is", len(hessian_matrix), "number of dofs is", number_of_degrees_of_freedom)

		return hessian_matrix

	def get_ionic_and_electronic_polarization_vectors(self):
		"""
		Returns two vectors, one containing the x, y, and z components of the ionic polarization, and another those of the electronic polarization.
		This return list looks like [vec_ionic, vec_electronic]
		"""

		ionic_polarization_indices = self.get_line_indices_containing_string('Ionic dipole moment: p[ion]')


		if len(ionic_polarization_indices) != 1:
			raise Exception("There must be one line containing the ionic polarization information.", len(ionic_polarization_indices))

		components_string = self[ionic_polarization_indices[0]].split('(')[1].split(')')[0]
		components_string = su.remove_extra_spaces(components_string)
		component_strings_list = components_string.split(' ')

		ionic_polarization_vector = [float(component) for component in component_strings_list]


		electronic_polarization_indices = self.get_line_indices_containing_string('Total electronic dipole moment: p[elc]')

		if len(electronic_polarization_indices) != 1:
			raise Exception("There must be one line containing the electronic polarization information.", len(electronic_polarization_indices))

		components_string = self[electronic_polarization_indices[0]].split('(')[1].split(')')[0]
		components_string = su.remove_extra_spaces(components_string)
		component_strings_list = components_string.split(' ')

		electronic_polarization_vector = [float(component) for component in component_strings_list]

		return [np.array(ionic_polarization_vector), np.array(electronic_polarization_vector)]