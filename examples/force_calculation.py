from fpctoolkit.structure.structure import Structure
from fpctoolkit.structure.perovskite import Perovskite
from fpctoolkit.workflow.vasp_run import VaspRun
from fpctoolkit.io.vasp.incar_maker import IncarMaker
from fpctoolkit.io.vasp.kpoints import Kpoints
from fpctoolkit.io.vasp.vasp_input_set import VaspInputSet



a = 3.79
Nx = 2
Ny = 2
Nz = 2



vasp_run_inputs_dictionary = {
	'kpoint_scheme': 'Monkhorst',
	'kpoint_subdivisions_list': [2, 2, 2],
	}

custom_incar_inputs = {
	'encut': 800
}


initial_structure=Perovskite(supercell_dimensions=[Nx, Ny, Nz], lattice=[[a*Nx, 0.0, 0.0], [0.0, a*Ny, 0.0], [0.0, 0.0, a*Nz]], species_list=['Sr', 'Ti', 'O'])


force_calculation_path = './dfpt_force_calculation'

kpoints = Kpoints(scheme_string=self.vasp_run_inputs['kpoint_scheme'], subdivisions_list=self.vasp_run_inputs['kpoint_subdivisions_list'])
incar = IncarMaker.get_dfpt_hessian_incar(custom_incar_inputs)

input_set = VaspInputSet(structure, kpoints, incar, auto_change_lreal=False, auto_change_npar=False)


dfpt_force_run = VaspRun(path=force_calculation_path, structure=initial_structure, input_set=input_set)


dfpt_force_run.update()