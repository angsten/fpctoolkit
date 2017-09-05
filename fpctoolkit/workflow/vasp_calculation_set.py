#from fpctoolkit.workflow.vasp_calculation_set import VaspCalculationSet


from fpctoolkit.util.path import Path

class VaspCalculationSet(object):
	"""
	Abstract calculation set class - any collection of vasp calculations.

	These runs operate in paralell/series like so:

	vasp_calculations_list = [vasp_calc_1, vasp_calc_2, [vcalc_3, vcalc_3_2], vcalc_4] ...]

	vcalc_2 waits for 1 to finish, but vcalc 3 and 3_2 both go at the same time.
	vcalc_4 waits for both previous two to finish.

	Calculations sets are just lists of calculations, and can thus be added together

	v_set_total = vrelax_set
	v_set_total += v_nmr_set #keeps same path as v_set_total, adds on new runs
	"""

	def __init__(self, path, vasp_calculations_list=None):
		self.path = path
		self.vasp_calculations_list = vasp_calculations_list




	def update(self):
		Path.make(self.path)
		
		complete = True
		for vasp_calculation_parallel_group in self.vasp_calculations_list:
			for vasp_calculation in vasp_calculation_parallel_group:
				if not vasp_calculation.update():
					complete = False

			if not complete:
				return False

		return True


	def complete(self):
		for vasp_calculation in self.vasp_calculations_list:
			if not vasp_calculation.complete:
				return False

		return True

	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)

	def __iadd__(self, new_vasp_calcualtions_list):
		self.vasp_calculations_list = self.vasp_calculations_list + new_vasp_calcualtions_list
		return self

