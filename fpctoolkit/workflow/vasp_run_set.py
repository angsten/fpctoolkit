



class VaspRunSet(object):
	"""
	Abstract run set class - any collection of vasp runs.

	Example child class: VaspRelaxation

	Complete and update and others must be implemented in child classes.
	"""

	def complete(self):
		pass

	def update(self):
		pass