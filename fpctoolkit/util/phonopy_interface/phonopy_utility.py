#import fpctoolkit.util.phonopy_interface.phonopy_utility as phonopy_utility

from phonopy.interface.vasp import read_vasp, write_vasp
from phonopy.interface.vasp import parse_set_of_forces

from fpctoolkit.structure.structure import Structure

def convert_structure_to_phonopy_atoms(structure, temporary_write_path):
	"""
	Takes structure, a Structure instance, and returns a PhonopyAtoms class (phonopy's representation of structures)

	temporary_write_path is where the structure is temporarily written to for purposes of conversion. This should be a safe
	path that won't overwrite other items. This path is deleted at the end.
	"""

	Structure.validate(structure)

	Path.validate_does_not_exist(temporary_write_path)
	Path.validate_writeable(temporary_write_path)

	structure.to_poscar_file_path(temporary_write_path)
	phonopy_structure = read_vasp(temporary_write_path)

	Path.remove(temporary_write_path)

	return phonopy_structure



def convert_phonopy_atoms_to_structure(phonopy_atoms_structure, temporary_write_path):
	"""
	Converts phonopy's representation of a structure to an instance of Structure.

	temporary_write_path is where the phonopy atoms structure is temporarily written to for purposes of conversion. This should be a safe
	path that won't overwrite other items. This path is deleted at the end.
	"""

	Path.validate_does_not_exist(temporary_write_path)
	Path.validate_writeable(temporary_write_path)

	write_vasp(temporary_write_path, phonopy_atoms_structure)

	structure_poscar_file = File(temporary_write_path)
	structure_poscar_file.insert(5, " ".join(initial_structure.get_species_list())) #phonopy uses bad poscar format
	structure_poscar_file.write_to_path()

	final_structure = Structure(temporary_write_path)
	
	Path.remove(temporary_write_path)

	Structure.validate(final_structure)

	return final_structure