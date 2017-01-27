

from fpctoolkit.io.file import File
import fpctoolkit.util.string_util as su

class Outcar(File):
	
	run_complete_string = "Total CPU time used (sec):"
	ionic_step_complete_string = "aborting loop because EDIFF is reached"
	total_energy_string = "energy(sigma->0)"

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


	def get_ionic_energies(self):
		"""Returns list of energies (one for each ionic step) currently present in outcar"""

		ionic_step_data_start_line_indices = self.get_line_indices_containing_string(Outcar.ionic_step_complete_string)
		print ionic_step_data_start_line_indices

	def get_calculation_time_in_core_hours(self):
		"""In cpu*hours. Good for comparing speed up when moving from smaller to larger number of cores"""

		return (self.get_total_cpu_time() / self.get_number_of_cores()) / 3600.0

	def get_number_of_cores(self):
		"""Returns number of cores recorded in outcar"""

		core_count_line = self.get_lines_containing_string("total cores") #may be fenrir specific!
		core_count_line = su.remove_extra_spaces(core_count_line)
		return int(core_count_line.split(' ')[2])

	def get_total_cpu_time(self):
		"""Returns number after Total CPU time used (sec): string"""

		cpu_time_line = self.get_lines_containing_string("Total CPU time used (sec):")
		cpu_time_line = su.remove_extra_spaces(cpu_time_line).strip()
		return float(cpu_time_line.split(' ')[5])