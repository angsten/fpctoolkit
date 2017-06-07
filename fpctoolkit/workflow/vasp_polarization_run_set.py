#from fpctoolkit.workflow.vasp_polarization_run_set import VaspPolarizationRunSet

from fpctoolkit.io.file import File
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.potcar import Potcar
from fpctoolkit.io.vasp.poscar import Poscar
from fpctoolkit.io.vasp.incar import Incar
from fpctoolkit.structure.structure import Structure
from fpctoolkit.io.vasp.outcar import Outcar
from fpctoolkit.util.path import Path
from fpctoolkit.util.queue_adapter import QueueAdapter, QueueStatus
import fpctoolkit.util.string_util as su

class VaspPolarizationRunSet(object):
	"""
	Class wrapper for vasp polarization calculations.

	This uses the Berry phase approach to calculate the change in total polarization (sum of ionic and electronic) in going from a reference structure to a distorted structure (with the same lattice, only atomic positions 
	should be different).

	The shorted polarization vector is always found, because polarization is defined to be unique within modulo (e*R)/omega, where R can be any sum of lattice vectors, and omega is the cell volume. This means this run set
	may not give the correct polarization vector if the true vector exceeds this fundamental vector in length (but this is rare).
	"""

	def __init__(self, path, reference_structure, distorted_structure, vasp_run_inputs_dictionary):
		"""
		reference_structure should be a Structure instance with the same lattice as distorted structure. Usually this reference is chosen to be centrosymmetry (like ideal perovskite) so that 
		absolute polarizations of the distorted structure can be caluclated.

		distorted_structure should be a Structure instance with the same lattice as the reference structure, but some of the atoms shifted to cause a change in polarization.
		"""

		Structure.validate(reference_structure)
		Structure.validate(distorted_structure)


		if not reference_structure.lattice.equals(distorted_structure.lattice):
			raise Exception("Warning: It's very difficult to interpret polarization results when the lattices of the reference and distorted structures are not equal. This is likely an error.", reference_structure.lattice, distorted_structure.lattice)


		self.path = path
		self.reference_structure = reference_structure
		self.distorted_structure = distorted_structure
		self.vasp_run_inputs = copy.deepcopy(vasp_run_inputs_dictionary)
		self.vasp_run_list = []

		Path.make(path)

		self.initialize_vasp_runs()


	def initialize_vasp_runs(self):
		"""
		Creates two vasp runs - one for the reference structure polarization calculation, and one for the distorted structure polarization calculation.
		"""

		reference_polarization_path = self.get_extended_path('reference_polarization')
		distorted_polarization_path = self.get_extended_path('distorted_polarization')

		if not Path.exists(reference_polarization_path):
			self.create_new_vasp_run(reference_polarization_path, self.reference_structure)

		if not Path.exists(distorted_polarization_path):
			self.create_new_vasp_run(distorted_polarization_path, self.distorted_structure)		


	def create_new_vasp_run(self, path, structure):
		"""
		Creates a polarization calculation at path using structure as the initial structure and self.vasp_run_inputs as the run inputs.
		"""

		run_inputs = copy.deepcopy(self.vasp_run_inputs)

		if 'submission_node_count' in run_inputs:
			node_count = run_inputs.pop('submission_node_count')
		else:
			node_count = None

		kpoints = Kpoints(scheme_string=run_inputs.pop('kpoint_scheme'), subdivisions_list=run_inputs.pop('kpoint_subdivisions_list'))
		incar = IncarMaker.get_lcalcpol_incar(run_inputs)

		input_set = VaspInputSet(structure, kpoints, incar, auto_change_lreal=('lreal' not in run_inputs), auto_change_npar=('npar' not in run_inputs))


		if node_count != None:
			input_set.set_node_count(node_count)

			# if 'npar' not in run_inputs:
			# 	input_set.set_npar_from_number_of_cores()

		vasp_run = VaspRun(path=path, input_set=input_set)

		self.vasp_run_list.append(vasp_run)

	def update(self):
		"""
		Runs update on all force calculations until they are all complete. 
		"""

		if not self.complete:
			for vasp_run in self.vasp_run_list:
				vasp_run.update()


	def get_change_in_polarization(self):

		if not self.complete:
			return None

		ref_volume = getVolume(os.path.join(ref_path,'OUTCAR')) #in Angstroms cubed
		ref_lattice = vaspio.poscar(os.path.join(ref_path,'POSCAR')).lattice
		pol_volume = getVolume(os.path.join(pol_path,'OUTCAR')) #in Angstroms cubed

		pol_lattice = vaspio.poscar(os.path.join(pol_path,'POSCAR')).lattice


		e = -1.6021766209*10**-19 #negative because vasp outputs in e, not abs value of e
		angstroms_sq_per_meter_sq = 10**20

		ref_pol = get_polarization(ref_path) #now holds reference ionic and electronic polarization in e*A
		ref_ion_pol = vector(ref_pol[0])
		ref_elec_pol = vector(ref_pol[1])
		ref_total_pol = ref_ion_pol.add(ref_elec_pol)

		a_ref = vector(ref_lattice[0])
		b_ref = vector(ref_lattice[1])
		c_ref = vector(ref_lattice[2])

		changed_pol = get_polarization(pol_path)
		changed_ion_pol = vector(changed_pol[0])
		changed_elec_pol = vector(changed_pol[1])
		changed_total_pol = changed_ion_pol.add(changed_elec_pol)

		#    print "Reference Lattice: " + str(ref_lattice)
		#    print "Deformed Lattice: " + str(pol_lattice)
		#    print
		'''
		print "\tReference Ionic Polarization: " + str(ref_ion_pol.getArray())
		print "\tDeformed Ionic Polarization:  " + str(changed_ion_pol.getArray())
		print
		print "\tReference Electronic Polarization: " + str(ref_elec_pol.getArray())
		print "\tDeformed Electronic Polarization:  " + str(changed_elec_pol.getArray())
		print
		'''
		ref_conv_factor = e*(1/ref_volume)*angstroms_sq_per_meter_sq
		change_conv_factor = e*(1/pol_volume)*angstroms_sq_per_meter_sq
		diff_ion_pol = (changed_ion_pol.scale(change_conv_factor)).subtract(ref_ion_pol.scale(ref_conv_factor))
		diff_elec_pol = (changed_elec_pol.scale(change_conv_factor)).subtract(ref_elec_pol.scale(ref_conv_factor))
		pol_total = diff_ion_pol.add(diff_elec_pol)
		#print "\tChange in Polarization Before Shift: " + str(pol_total.getArray())

		search_range_min = -3
		search_range_max = 3
		min_mag = 100000000
		vec = None
		for i in range(search_range_min,search_range_max):
			for j in range(search_range_min,search_range_max):
				for k in range(search_range_min,search_range_max):
					ref_vec = (((a_ref.scale(2*i)).add(b_ref.scale(2*j))).add(c_ref.scale(2*k))) #polarization defined within modulo eR/omega

					shifted_changed_pol = changed_total_pol.add(ref_vec)

					diff_vec = shifted_changed_pol.subtract(ref_total_pol) #vector between two choice branch lattice points
					mag = diff_vec.magnitude()

					if mag < min_mag:
						min_mag = mag
						vec = vector(diff_vec.getArray()) #this is shortest change in polarization found and thus most likely polariation vect

		return (vec.scale(ref_conv_factor)).getArray()








		def get_polarization(run_path):
			ionic_pol = []
			elec_pol = []

			out_path = os.path.join(run_path,'OUTCAR')
			file = open(out_path,'rb')
			lines = file.readlines()
			file.close()

			volume = getVolume(out_path)
			coulumbs_per_e = -1.6021766209*10**-19 #negative because vasp outputs in e but not abs value of e
			angstroms_sq_per_meter_sq = 10**20

			for i in range(len(lines)-1,-1,-1):
				if not lines[i].find('Ionic dipole moment: p[ion]') == -1:
					ionic_pol = extractNumbers(lines[i])
				if not lines[i].find('Total electronic dipole moment: p[elc]=') == -1:
					elec_pol = extractNumbers(lines[i])

			if len(elec_pol) > 0 and len(ionic_pol) > 0:
				break

			'''
			for i in range(0,3):
			ionic_pol[i] *= coulumbs_per_e*(1/volume)*angstroms_sq_per_meter_sq #converted change in polarization in C/m^2 for this component
			elec_pol[i] *= coulumbs_per_e*(1/volume)*angstroms_sq_per_meter_sq
			'''
			return [ionic_pol,elec_pol]


	@property
	def complete(self):
		for vasp_run in self.vasp_run_list:
			if not vasp_run.complete:
				return False

		return True

	def get_extended_path(self, relative_path):
		return Path.join(self.path, relative_path)