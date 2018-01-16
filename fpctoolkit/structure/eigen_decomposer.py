#import fpctoolkit.structure.eigen_decomposer as eig_dec

from fpctoolkit.phonon.eigen_structure import EigenStructure
from fpctoolkit.util.path import Path
from fpctoolkit.phonon.hessian import Hessian
from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.displacement_vector import DisplacementVector
from fpctoolkit.structure.lattice import Lattice
from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.workflow.vasp_static_run_set import VaspStaticRunSet

import sys
import numpy as np
import copy


fex = np.array([
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.12796, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 0.24619, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000,
	 -0.09810, 0.00000, 0.00000,
	 -0.13855, 0.00000, 0.00000
	 ])

fey = np.array([
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.12796, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  0.24619, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.13855, 0.00000,
	0.00000,  -0.09810, 0.00000,
	0.00000,  -0.13855, 0.00000
	])

# fez = np.array([
	# 0.00000  0.00000  0.12796
	# 0.00000  0.00000  0.12796
	# 0.00000  0.00000  0.12796
	# 0.00000  0.00000  0.12796
	# 0.00000  0.00000  0.12796
	# 0.00000  0.00000  0.12796
	# 0.00000  0.00000  0.12796
	# 0.00000  0.00000  0.12796
	# 0.00000  0.00000  0.24619
	# 0.00000  0.00000  0.24619
	# 0.00000  0.00000  0.24619
	# 0.00000  0.00000  0.24619
	# 0.00000  0.00000  0.24619
	# 0.00000  0.00000  0.24619
	# 0.00000  0.00000  0.24619
	# 0.00000  0.00000  0.24619
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.09810
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.09810
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.09810
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.09810
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.09810
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.09810
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.09810
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.13855
	# 0.00000  0.00000  -0.09810
	# 0.00000  0.00000  -0.13855
# 	])

fez = np.array([
	 0.00000,  0.00000, -0.19976,
	 0.00000,  0.00000, -0.19976,
	 0.00000,  0.00000, -0.19976,
	 0.00000,  0.00000, -0.19976,
	 0.00000,  0.00000, -0.19976,
	 0.00000,  0.00000, -0.19976,
	 0.00000,  0.00000, -0.19976,
	 0.00000,  0.00000, -0.19976,
	 0.00000,  0.00000, -0.17470,
	 0.00000,  0.00000, -0.17470,
	 0.00000,  0.00000, -0.17470,
	 0.00000,  0.00000, -0.17470,
	 0.00000,  0.00000, -0.17470,
	 0.00000,  0.00000, -0.17470,
	 0.00000,  0.00000, -0.17470,
	 0.00000,  0.00000, -0.17470,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.05308,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.05308,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.05308,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.05308,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.05308,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.05308,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.05308,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.16087,
	 0.00000,  0.00000,  0.05308,
	 0.00000,  0.00000,  0.16087
	  ])


aminus = np.array([
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000, -0.25000,
	  0.00000,  0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.25000,
	  0.00000, -0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.25000,
	  0.00000, -0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000, -0.25000,
	  0.00000,  0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.25000,
	  0.00000, -0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000, -0.25000,
	  0.00000,  0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000, -0.25000,
	  0.00000,  0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000,
	  0.00000,  0.00000,  0.25000,
	  0.00000, -0.25000,  0.00000,
	  0.00000,  0.00000,  0.00000
	  ])

bminus = np.array([
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000, 0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000, 0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000, 0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000, 0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000
	 ])

cminus = np.array([
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.25000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000, -0.25000,  0.00000,
	-0.2500,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.25000,  0.00000,
	-0.2500,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.25000,  0.00000,
	0.25000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000, -0.25000,  0.00000,
	-0.2500,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.25000,  0.00000,
	0.25000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000, -0.25000,  0.00000,
	0.25000,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000, -0.25000,  0.00000,
	-0.2500,  0.00000,  0.00000,
	0.00000,  0.00000,  0.00000,
	0.00000,  0.25000,  0.00000
	])

aplus = np.array([
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000, -0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000, -0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000, -0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000, -0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.25000,  0.00000,
	 0.00000,  0.00000,  0.00000
	 ])

bplus = np.array([
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000, -0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000, -0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000, -0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000, -0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000,
	 0.00000,  0.00000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000, -0.25000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.25000
	 ])

cplus = np.array([
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.25000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000, -0.25000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000, -0.25000,  0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.25000,  0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.25000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000, -0.25000,  0.00000,
	 0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000, -0.25000,  0.00000,
	 -0.25000,  0.00000,  0.00000,
	 0.00000,  0.00000,  0.00000,
	 0.00000,  0.25000,  0.00000
	 ])

fex *= 1.0/(np.linalg.norm(fex))
fey *= 1.0/(np.linalg.norm(fey))
fez *= 1.0/(np.linalg.norm(fez))

cplus *= -1.0


translational_vector_x = []
translational_vector_y = []
translational_vector_z = []


for i in range(120):
	if i%3 == 0:
		translational_vector_x.append(1.0)
		translational_vector_y.append(0.0)
		translational_vector_z.append(0.0)
	if i%3 == 0:
		translational_vector_x.append(0.0)
		translational_vector_y.append(1.0)
		translational_vector_z.append(0.0)
	if i%3 == 0:
		translational_vector_x.append(0.0)
		translational_vector_y.append(0.0)
		translational_vector_z.append(1.0)

translational_vector_x = np.array(translational_vector_x)
translational_vector_y = np.array(translational_vector_y)
translational_vector_z = np.array(translational_vector_z)

translational_vector_x /= np.linalg.norm(translational_vector_x)
translational_vector_y /= np.linalg.norm(translational_vector_y)
translational_vector_z /= np.linalg.norm(translational_vector_z)


eigen_basis_vectors_list = [aminus, bminus, cminus, aplus, bplus, cplus, fex, fey, fez]#, translational_vector_x, translational_vector_y, translational_vector_z]

labels_list = ['a-', 'b-', 'c-', 'a+', 'b+', 'c+', 'FEx', 'FEy', 'FEz']


# print np.dot(fex, bplus)

# print
# print "magnitudes"

# for eig in eigen_basis_vectors_list:
# 	print "magnitude: ", np.linalg.norm(eig)

# 	for other_eig in eigen_basis_vectors_list:

# 		print "dot:", np.dot(eig, other_eig)



if __name__ == '__main__':
	pass
	# reference_structure_path = '../data/reference_structure.vasp'


	# reference_structure = Structure(reference_structure_path)


	# displacement_vector = cplus

	# displacement_vector *= 0.7

	# distorted_structure = DisplacementVector.displace_structure(reference_structure=reference_structure, displacement_vector=displacement_vector, displacement_coordinate_mode='Cartesian')

	# distorted_structure.to_poscar_file_path('../data/cplus.vasp')


	# relaxed_structure = Structure('../data/relaxed_structure.vasp')


	# relaxed_structure.lattice = copy.deepcopy(reference_structure.lattice)

	# total_displacement_vector_instance = DisplacementVector.get_instance_from_displaced_structure_relative_to_reference_structure(reference_structure=reference_structure, 
	# 		displaced_structure=relaxed_structure, coordinate_mode='Cartesian')

	# total_displacement_vector = total_displacement_vector_instance.to_numpy_array()

	# print "a-      b-       c-       a+      b+       c+     FEx      FEy      FEz"

	# for basis_vector in eigen_basis_vectors_list:
	# 	projection = np.dot(basis_vector, total_displacement_vector)

	# 	print str(round(projection,4)) + '   ',

	#eigen_amplitude_analysis_hessian = Hessian(outcar=Outcar("./dfpt_outcar"))
	#eigen_amplitude_analysis_reference_structure = Structure("./reference_structure")
	#eigen_structure = EigenStructure(reference_structure=eigen_amplitude_analysis_reference_structure, hessian=eigen_amplitude_analysis_hessian)

	#eigen_structure.set_strains_and_amplitudes_from_distorted_structure(relaxed_structure)
	#relaxed_eigen_chromosome =  eigen_structure.get_list_representation()


	#print " ".join(str(round(x, 3)) for x in relaxed_eigen_chromosome[:20])


def print_labels():
	print "      ".join(labels_list)

def get_nine_common_amplitudes(distorted_structure):


	reference_structure = Perovskite(supercell_dimensions=[2, 2, 2], lattice = distorted_structure.lattice, species_list=distorted_structure.get_species_list())

	total_displacement_vector_instance = DisplacementVector.get_instance_from_displaced_structure_relative_to_reference_structure(reference_structure=reference_structure, 
			displaced_structure=distorted_structure, coordinate_mode='Cartesian')

	total_displacement_vector = total_displacement_vector_instance.to_numpy_array()


	for basis_vector in eigen_basis_vectors_list:
		projection = np.dot(basis_vector, total_displacement_vector)

		print str(round(projection,4)) + '   ',

def get_fraction_of_displacements_for_nine_common_modes(distorted_structure):

	reference_structure = Perovskite(supercell_dimensions=[2, 2, 2], lattice=distorted_structure.lattice, species_list=distorted_structure.get_species_list())

	total_displacement_vector_instance = DisplacementVector.get_instance_from_displaced_structure_relative_to_reference_structure(reference_structure=reference_structure, 
			displaced_structure=distorted_structure, coordinate_mode='Cartesian')

	total_displacement_vector = total_displacement_vector_instance.to_numpy_array()

	total_displacement_magnitude = sum([abs(x) for x in total_displacement_vector])

	print "Total displacement magnitude is " + str(total_displacement_magnitude) + " angstroms"


	for basis_vector in eigen_basis_vectors_list:
		projection = np.dot(basis_vector, total_displacement_vector)

		#contribution_vector = projection*basis_vector

		#basis_total_displacement_magnitude_contribution = np.linalg.norm(contribution_vector) #sum([abs(x) for x in contribution_vector])

		#fractions.append(float(basis_total_displacement_magnitude_contribution/total_displacement_magnitude))

		fractions.append(abs(projection)/total_displacement_magnitude)

	return fractions



def get_eigen_values(base_path, reference_structure, eigen_indices_list, vasp_run_inputs_dictionary, displacement_magnitude_factor):

	for eigen_index in eigen_indices_list:

		second_derivative = get_displacement_second_derivative(Path.join(base_path, 'eigen_index_' + str(eigen_index)), reference_structure, eigen_index, vasp_run_inputs_dictionary, displacement_magnitude_factor)

		print labels_list[eigen_index], second_derivative, " "




def get_displacement_second_derivative(path, reference_structure, eigen_index, vasp_run_inputs_dictionary, displacement_magnitude_factor):
	"""
	Determines the second derivative of the energy w.r.t. the given displacement variable for structure.

	Returns None if not done yet
	"""

	# vasp_run_inputs_dictionary = {
	# 		'kpoint_scheme': 'Monkhorst',
	# 		'kpoint_subdivisions_list': [3, 3, 3],
	# 		'encut': 600,
	# 		'ediff': 1e-7,
	# 		'addgrid': True,
	# 		'lreal': False
	# 	}

	central_difference_coefficients_dictionary = {}

	central_difference_coefficients_dictionary['1'] =  {'factors':[0.0, 1.0, -1.0], 'perturbations_list': [[1.0]]} #NOTE!! assumes centrosymmetry - only works if atoms are at ideal perov positions


	perturbed_structures_list = []

	for perturbation_magnitude in central_difference_coefficients_dictionary['1']['perturbations_list']:

		displacement_vector = eigen_basis_vectors_list[eigen_index]*perturbation_magnitude*displacement_magnitude_factor

		distorted_structure = DisplacementVector.displace_structure(reference_structure, displacement_vector, displacement_coordinate_mode='Cartesian')

		perturbed_structures_list.append(distorted_structure)

	vasp_static_run_set = VaspStaticRunSet(path=path, structures_list=perturbed_structures_list, vasp_run_inputs_dictionary=vasp_run_inputs_dictionary)


	if vasp_static_run_set.complete:

		vasp_static_run_set.delete_wavecars_of_completed_runs()

		term_factors_list = central_difference_coefficients_dictionary['1']['factors']


		force_sum = get_force_sums(vasp_static_run_set, eigen_index)[0] #THIS ASSUMES CENTROSYMMETRY AND ONLY ONE ELEMENT IN FORCE SUMS LIST

		force_sums_list = [0.0, force_sum, -1.0*force_sum] ################assumes centrosymmetry and one element in force sumes list

		numerator = sum(map(lambda x, y: -x*y, term_factors_list, force_sums_list))
		denominator = 2.0*displacement_magnitude_factor

		return numerator/denominator

	else:
		vasp_static_run_set.update()

		return None


def get_force_sums(vasp_static_run_set, eigen_index):
	"""
	Returns a list of weighted force sums for each static calculation. Basically, this takes -1.0*eigenvector of the first displacement expansion term and dots
	it with the force set of the run. This gives dE/dA
	"""

	basis_vector = eigen_basis_vectors_list[eigen_index]

	forces_sums_list = []

	forces_lists = vasp_static_run_set.get_forces_lists()


	return [np.dot(np.array(forces_list), basis_vector) for forces_list in forces_lists]