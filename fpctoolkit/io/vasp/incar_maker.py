#from fpctoolkit.io.vasp.incar_maker import IncarMaker

from fpctoolkit.io.vasp.incar import Incar

class IncarMaker(object):
	"""Helper class for creating standard incars with slight modifications.

	In general, functions have a new_parameters argument. This is a dictionary
	to override certain parameters in the standard set.

	"""

	@staticmethod
	def get_static_incar(custom_parameters_dictionary=None):
		incar = Incar()

		#optional parameters that can be overwritten by the user
		incar['ibrion'] = -1
		incar['nsw'] = 0
		incar['nelmin'] = 6 #helps with force accuracy
		incar['isif'] = 2 #by default, calculate the stress tensor (atoms won't move still)
		incar['ismear'] = 0
		incar['sigma'] = 0.02
		incar['prec'] = 'Accurate'
		incar['ediff'] = 1.0e-6
		incar['encut'] = 600
		incar['lasph'] = True
		# incar['lwave'] = False
		# incar['lcharg'] = False

		incar.modify_from_dictionary(custom_parameters_dictionary)

		return incar

	@staticmethod
	def get_external_relaxation_incar(custom_parameters_dictionary=None):
		incar = Incar()

		#optional parameters that can be overwritten by the user
		incar['ibrion'] = 2
		incar['nsw'] = 151
		incar['nelmin'] = 6 #helps with force accuracy
		incar['isif'] = 3 #by default, calculate the stress tensor (atoms won't move still)
		incar['ismear'] = 0
		incar['sigma'] = 0.02
		incar['prec'] = 'Accurate'
		incar['ediff'] = 1.0e-6
		incar['encut'] = 600
		incar['lwave'] = True
		incar['lasph'] = True
		# incar['lcharg'] = False

		incar.modify_from_dictionary(custom_parameters_dictionary)

		return incar


	@staticmethod
	def get_accurate_forces_incar(custom_parameters_dictionary=None):
		"""
		Used for a very accurate static forces calculation (such as for phonons) on a single structure.
		"""

		incar = IncarMaker.get_static_incar()

		incar['ediff'] = 1.0e-9
		incar['addgrid'] = True
		incar['lreal'] = False #must be false for any sized supercell


		incar.modify_from_dictionary(custom_parameters_dictionary)

		return incar


	@staticmethod
	def get_lepsilon_incar(custom_parameters_dictionary=None):
		"""
		Generates an incar to be used with an lepsilon run that generate things like the born effective charge, piezoelectric, and dielectric tensors.
		"""

		incar = IncarMaker.get_static_incar()
		incar['ediff'] = 1.0e-7
		incar['lepsilon'] = True
		del incar['npar'] #lepsilon runs are not parallelizable

		incar.modify_from_dictionary(custom_parameters_dictionary)

		return incar


	@staticmethod
	def get_dfpt_hessian_incar(custom_parameters_dictionary=None):
		"""
		Generates an incar to be used for getting the Hessian force constants matrix using dfpt. Ibrion = 8 uses symmetry to simplify the calculation, ibrion = 7 doesn't.
		"""

		incar = IncarMaker.get_static_incar()
		incar['ibrion'] = 8
		incar['ediff'] = 1.0e-8
		incar['addgrid'] = True
		incar['lreal'] = False #must be false for any sized supercell
		incar['nsw'] = 1

		del incar['npar'] #lepsilon runs are not parallelizable when symmetry is on

		incar.modify_from_dictionary(custom_parameters_dictionary)

		return incar


	@staticmethod
	def get_lcalcpol_incar(custom_parameters_dictionary=None):
		"""
		Generates an incar to be used for getting the electronic and ionic contributions to macroscopic polarization using the Berry phase formalism.
		"""

		incar = IncarMaker.get_static_incar(custom_parameters_dictionary)
		del incar['ibrion']
		del incar['nsw']
		del incar['npar'] #lcalcpol runs are not parallelizable when symmetry is on

		incar['lcalcpol'] = True
		incar['dipol'] = '0.125 0.125 0.125' #this should be a point of minimum polarization in the cell ########################
		incar['isif'] = 2

		return incar

	@staticmethod
	def get_nmr_incar(custom_parameters_dictionary=None):

		incar = IncarMaker.get_static_incar()
		del incar['ibrion']
		del incar['nsw']
		del incar['npar'] #lcalcpol runs are not parallelizable when symmetry is on

		incar['lchimag'] = True
		incar['ediff'] = 1e-10
		incar['dq'] = 0.001
		incar['ichibare'] = 1
		incar['lnmr_sym_red'] = True

		incar.modify_from_dictionary(custom_parameters_dictionary)

		return incar