import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from fpctoolkit.io.file import File
import fpctoolkit.util.string_util as su

file_path = 'C:\Users\Tom\Desktop\pvodosrefined666M'
file = File(file_path)


num_atoms = 5


def get_floats_list_from_string(line):
	return [float(x) for x in su.remove_extra_spaces(line.strip()).split(' ')]

# print file

tag_line = file[5]
fermi_energy = get_floats_list_from_string(tag_line)[3]

print "Fermi energy: " + str(fermi_energy)


section_indices = []

for i, line in enumerate(file):
	if line == tag_line:
		section_indices.append(i)
		

data_series = []
		
for i in range(len(section_indices)):

	start_index = section_indices[i]

	if i == (len(section_indices) - 1):
		end_index = len(file)
	else:
		end_index = section_indices[i+1]

	new_data_set = []

	for j in range(start_index+1, end_index):
		new_data_set.append(get_floats_list_from_string(file[j]))

	data_series.append(new_data_set)

energies_list = [x[0]-fermi_energy for x in data_series[0]]



total_dos_up = []
total_dos_down = []
total_dos = []

#get total dos
if len(data_series[0][0]) == 5: #columns are energy dos integrated dos

	for data in data_series[0]:
		dos_up_value = data[1]
		dos_down_value = -1.0*data[2]

		total_dos_up.append(dos_up_value)
		total_dos_down.append(dos_down_value)
		total_dos.append(data[1] + data[2])

pdos = [] #each index corresponds to the associated atom in the poscar, a set of dictionaries with keys like 's_up' or just 's' or 'px_down' or any of below and values as lists of dos vals
# s_up	s_down	px_up	px_down	py_up	py_down	pz up	pz down  	dxy up	dxy down	dyz up	dyz down	dz2 up	dz2 down	dxz up	dxz down	dx2 up	dx2 down

# get projected dos sets

if len(data_series[1][0]) == 19: #spin, columns are energy and those above, one set for each atom

	for i in range(num_atoms):
		new_pdos = {'s_up': [], 's_down': [], 'p_total': [], 'p_up': {'total': [], 'x': [], 'y': [], 'z': []}, 'p_down': {'total': [], 'x': [], 'y': [], 'z': []}, 'd_total': [], 'd_up': {'total': [], 'xy': [], 'yz': [], 'z2': [], 'xz': [], 'x2': []}, 'd_down': {'total': [], 'xy': [], 'yz': [], 'z2': [], 'xz': [], 'x2': []}}

		for data in data_series[i+1]:
			new_pdos['s_up'].append(data[1])
			new_pdos['s_down'].append(-1.0*data[2])

			new_pdos['p_up']['x'].append(data[3])
			new_pdos['p_down']['x'].append(-1.0*data[4])
			new_pdos['p_up']['y'].append(data[5])
			new_pdos['p_down']['y'].append(-1.0*data[6])
			new_pdos['p_up']['z'].append(data[7])
			new_pdos['p_down']['z'].append(-1.0*data[8])

			new_pdos['p_up']['total'].append(data[3] + data[5] + data[7])
			new_pdos['p_down']['total'].append(-1.0*(data[4] + data[6] + data[8]))

			new_pdos['p_total'].append(data[3] + data[4] + data[5] + data[6] + data[7] + data[8])

			new_pdos['d_up']['xy'].append(data[9])
			new_pdos['d_down']['xy'].append(-1.0*data[10])

			new_pdos['d_up']['yz'].append(data[11])
			new_pdos['d_down']['yz'].append(-1.0*data[12])

			new_pdos['d_up']['z2'].append(data[13])
			new_pdos['d_down']['z2'].append(-1.0*data[14])

			new_pdos['d_up']['xz'].append(data[15])
			new_pdos['d_down']['xz'].append(-1.0*data[16])

			new_pdos['d_up']['x2'].append(data[17])
			new_pdos['d_down']['x2'].append(-1.0*data[18])

			new_pdos['d_up']['total'].append(data[9] + data[11] + data[13] + data[15] + data[17])
			new_pdos['d_down']['total'].append(-1.0*(data[10] + data[12] + data[14] + data[16] + data[18]))

			new_pdos['d_total'].append(data[9] + data[11] + data[13] + data[15] + data[17] + data[10] + data[12] + data[14] + data[16] + data[18])


		pdos.append(new_pdos)





energy_min = -10
energy_max = 10
state_count_max = 10

title = 'PVO3 5-atom Ferromagnetic GGA HSE06 With Spin Polarization bulk 600eV encut 6x6x6M Kpoints precfock=normal no nkred'
labels = ['Total', 'V d-states', 'O1 p-states', 'O2 p-states']

# plt.suptitle('DOS')

# plt.plot(energies_list, total_dos, 'black', linewidth=2.0)

figure, sub_plots = plt.subplots(4, sharex=True)
figure.set_size_inches(12, 9, forward=True)

sub_plots[0].plot(energies_list, total_dos, 'black', linewidth=2.0)

sub_plots[0].axis([energy_min, energy_max, 0, state_count_max])

#sub_plots[0].plot(energies_list, total_dos_down, 'black', linewidth=2.0)

sub_plots[1].plot(energies_list, pdos[1]['d_up']['total'], 'black', linewidth=2.0)
sub_plots[1].plot(energies_list, pdos[1]['d_down']['total'], 'black', linewidth=2.0)

sub_plots[2].plot(energies_list, pdos[4]['p_total'], 'black', linewidth=2.0)
sub_plots[3].plot(energies_list, pdos[2]['p_total'], 'black', linewidth=2.0)

# sub_plots[2].plot(energies_list, pdos[4]['p'], 'black', linewidth=2.0)
# sub_plots[3].plot(energies_list, pdos[2]['p'], 'black', linewidth=2.0)


sub_plots[-1].set_xlabel('Energy (eV)', fontsize=18)
figure.text(0.04, 0.5, 'Density of States (states/eV*cell)', fontsize=18, va='center', rotation='vertical')

figure.subplots_adjust(hspace=0)

for i, plot in enumerate(sub_plots):
	for tick in plot.xaxis.get_major_ticks():
		tick.label.set_fontsize(14)
	for tick in plot.yaxis.get_major_ticks():
		tick.label.set_fontsize(14)
	plot.xaxis.set_tick_params(width=1.25, length=5) #set tick length and width
	plot.yaxis.set_tick_params(width=1.25, length=5)
	[spine.set_linewidth(1.5) for spine in plot.spines.itervalues()] #set border width

	plot.yaxis.get_major_ticks()[-1].set_visible(False)
	plot.axvline(x=0.0, color='r', linestyle='--')

	plot.text(0.88, 0.85, labels[i], verticalalignment='top', horizontalalignment='center', transform=plot.transAxes, color='black', fontsize=16)



# plt.savefig(pp, format='pdf')

figure.set_figwidth(8)
figure.set_figheight(8)
figure.patch.set_facecolor('white')
figure.text(0.5, 0.94, title, fontsize=16, ha='center')

plt.show()

# plt.clf()


