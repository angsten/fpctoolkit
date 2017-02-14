

from fpctoolkit.util.path import Path







"""
This program takes a perovskite structure of a given composition and searches for the global minimum
in the energy under given (100) epitaxial constraints (a and b lattice vectors equal in magnitude, normal, 
and fixed). The search is performed around the perfect cubic perovskite structure, and the A lattice is 
mostly preserved in this search as a roughly square lattice (if this were not so, the structure would not
persist without extremely high coherency energies as an epitaxial film).
"""



def update_epitaxial_100_structure_search():

	




if __name__ == "__main__":
	in_plane_lattice_constant = 15.6
	super_cell_dimensions_list = [4, 4, 1]
	species_list = ['K', 'V', 'O']

	main_path = Path.clean('./')





