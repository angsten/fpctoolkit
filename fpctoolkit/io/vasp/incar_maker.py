

from fpctoolkit.io.vasp.incar import Incar

class IncarMaker(object):
	"""Helper class for creating standard incars with slight modifications.

	In general, functions have a new_parameters argument. This is a dictionary
	to override certain parameters in the standard set.

	"""



	@staticmethod
	def get_static_incar(custom_parameters=None):
		incar = Incar()

		#optional parameters that can be overwritten by the user
		incar['ibrion'] = -1
		incar['nsw'] = 0
		incar['nelmin'] = 6 #helps with force accuracy
		incar['isif'] = 2 #by default, calculate the stress tensor (atoms won't move still)
		incar['ismear'] = 0
		incar['sigma'] = 0.01
		incar['prec'] = 'Accurate'
		incar['ediff'] = 0.000001
		incar['encut'] = 600
		incar['lreal'] = False
		incar['lwave'] = False
		incar['lcharg'] = False

		#load in user custom parameters
		if custom_parameters:
			for key, value in custom_parameters.items():
				incar[key] = value


		if not incar['ibrion'] == -1:
			raise Exception("IBRION must be -1 in a static calculation")

		if not incar['nsw'] == 0:
			raise Exception("NSW must be 0 in a static calculation")

		return incar