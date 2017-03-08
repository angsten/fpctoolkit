#from fpctoolkit.workflow.vasp_run_set import VaspRunSet


from fpctoolkit.util.path import Path
import cPickle

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

	def save(self):
		"""Saves self to a pickled file"""

		file = open(self.get_save_path(), 'w')
		file.write(cPickle.dumps(self.__dict__))
		file.close()

	def load(self):
		"""
		Loads the previously saved pickled instance of self at self.path. self.path is not overwritted by the load in case the run has since been moved.
		"""

		if not Path.exists(self.get_save_path()):
			raise Exception("Cannot load calculation set: no instance saved to file.")

		file = open(self.get_save_path(), 'r')
		data_pickle = file.read()
		file.close()

		previous_path = self.path
		self.__dict__ = cPickle.loads(data_pickle)
		self.path = previous_path #in case run is moved


	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)

	def get_save_path(self):
		return self.get_extended_path(".vasp_run_set_pickle")