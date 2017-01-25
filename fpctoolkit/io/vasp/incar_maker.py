



class IncarMaker(object):
	"""Helper class for creating standard incars with slight modifications.

	In general, functions have a new_parameters argument. This is a dictionary
	to override certain parameters in the standard set.

	"""



	@staticmethod
	def get_static_incar(new_parameters=None):
		incar = Incar()

		IBRION = 2
		ISIF = 3
		NSW = 191
		ISMEAR = 0
		SIGMA = 0.01
		LREAL = False
		LWAVE = True
		LCHARG = False
		NPAR = 2
		PREC = Normal
		EDIFF = 0.0004
		ENCUT = 400
		KSPACING = 1.0
		KGAMMA = False
		NELMIN = 4

		incar['ibrion'] = -1
		del incar['isif']
		incar['nsw'] = 0
		incar['ismear'] = 0
		incar['']