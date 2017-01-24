

from fpctoolkit.io.file import File

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

